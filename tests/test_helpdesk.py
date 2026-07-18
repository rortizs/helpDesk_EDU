from fastapi.testclient import TestClient


def client():
    from app.main import create_app
    return TestClient(create_app(database_url="sqlite://"))


def login(c, email, password):
    response = c.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_and_login():
    c = client()
    assert c.get("/api/health").json() == {"status": "ok"}
    token = c.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin123"}).json()
    assert token["token_type"] == "bearer"


def test_technician_can_close_ticket_through_explicit_close_endpoint():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    ticket = c.post("/api/tickets", headers=requester, json={"title": "Projector is broken", "description": "Room A101", "category": "Hardware", "priority": "High"})

    response = c.post(f"/api/tickets/{ticket.json()['id']}/close", headers=technician)

    assert response.status_code == 200
    assert response.json()["status"] == "Closed"


def test_ticket_history_endpoint_exposes_assignment_records_to_requester():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    ticket = c.post("/api/tickets", headers=requester, json={"title": "Projector is broken", "description": "Room A101", "category": "Hardware", "priority": "High"})
    ticket_id = ticket.json()["id"]
    assert c.patch(f"/api/tickets/{ticket_id}/assign", headers=technician, json={"assignee_id": 3}).status_code == 200

    response = c.get(f"/api/tickets/{ticket_id}/history", headers=requester)

    assert response.status_code == 200
    assert any(event["event_type"] == "assigned" and event["detail"] == "Assigned to Technician" for event in response.json()["items"])


def test_role_restriction_and_ticket_lifecycle():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    assert c.get("/api/users", headers=requester).status_code == 403
    ticket = c.post("/api/tickets", headers=requester, json={"title":"Projector is broken","description":"Room A101","category":"Hardware","priority":"High"})
    assert ticket.status_code == 201
    ticket_id = ticket.json()["id"]
    assert c.get("/api/tickets", headers=requester).json()["items"][0]["id"] == ticket_id
    assert c.get(f"/api/tickets/{ticket_id}", headers=requester).status_code == 200
    assert c.patch(f"/api/tickets/{ticket_id}/assign", headers=technician, json={"assignee_id": 3}).status_code == 200
    assert c.post(f"/api/tickets/{ticket_id}/comments", headers=requester, json={"body":"Please help soon"}).status_code == 201
    assert c.patch(f"/api/tickets/{ticket_id}/status", headers=technician, json={"status":"In Progress"}).json()["status"] == "In Progress"
    detail = c.get(f"/api/tickets/{ticket_id}", headers=requester).json()
    assert len(detail["comments"]) == 1 and any(event["event_type"] == "status_changed" for event in detail["history"])


def test_required_frontend_pages_render_their_page_specific_content():
    c = client()

    assert "HelpDesk EDU login" in c.get("/login").text
    assert "Support for every learning moment" in c.get("/").text
    c.post("/login", data={"email": "technician@example.com", "password": "technician123"})
    for path, content in [("/workspace", "HelpDesk EDU Dashboard"), ("/tickets", "HelpDesk EDU Tickets")]:
        response = c.get(path)
        assert response.status_code == 200
        assert content in response.text


def test_public_landing_invites_customers_to_enter_the_portal():
    c = client()

    response = c.get("/")

    assert response.status_code == 200
    assert "Support for every learning moment" in response.text
    assert 'href="/portal"' in response.text
    assert "bootstrap@5" in response.text


def test_customer_portal_requires_a_requester_session_and_tracks_that_requesters_ticket():
    c = client()

    unauthenticated = c.get("/portal", follow_redirects=False)
    assert unauthenticated.status_code == 303
    assert unauthenticated.headers["location"] == "/login"

    assert c.post("/login", data={"email": "requester@example.com", "password": "requester123"}, follow_redirects=False).status_code == 303
    created = c.post(
        "/portal/tickets/new",
        data={"title": "Portal-owned request", "description": "Created by the signed-in customer.", "category": "Access", "priority": "High"},
        follow_redirects=False,
    )

    assert created.status_code == 303
    assert created.headers["location"].startswith("/portal/tickets/")
    assert "Portal-owned request" in c.get(created.headers["location"]).text
    assert "Portal-owned request" in c.get("/portal/tickets").text


def test_customer_portal_and_staff_workspace_keep_separate_session_boundaries():
    c = client()

    requester_login = c.post(
        "/login",
        data={"email": "requester@example.com", "password": "requester123"},
        follow_redirects=False,
    )
    assert requester_login.headers["location"] == "/portal"
    assert c.get("/workspace", follow_redirects=False).headers["location"] == "/login"
    assert "Customer portal" in c.get("/portal").text

    staff = client()
    staff_login = staff.post(
        "/login",
        data={"email": "technician@example.com", "password": "technician123"},
        follow_redirects=False,
    )
    assert staff_login.headers["location"] == "/workspace"
    workspace = staff.get("/workspace")
    assert workspace.status_code == 200
    assert "AdminLTE" in workspace.text
    assert "app-sidebar" in workspace.text
    assert "bootstrap@5" not in workspace.text


def test_frontend_staff_ticket_queue_renders_requester_created_tickets():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    c.post(
        "/api/tickets",
        headers=requester,
        json={
            "title": "Queue-visible requester ticket",
            "description": "Staff should see requester-created work.",
            "category": "Access",
            "priority": "Critical",
        },
    )
    c.post("/login", data={"email": "technician@example.com", "password": "technician123"})

    response = c.get("/tickets")

    assert response.status_code == 200
    assert "Queue-visible requester ticket" in response.text
    assert "Open" in response.text
    assert "Critical" in response.text
    assert "Requester" in response.text
    assert "Unassigned" in response.text


def test_frontend_ticket_form_creates_ticket_and_redirects_to_detail():
    c = client()
    c.post("/login", data={"email": "technician@example.com", "password": "technician123"})

    response = c.post(
        "/tickets/new",
        data={
            "title": "Cannot access virtual campus",
            "description": "The student cannot access the virtual campus with current credentials.",
            "category": "Access",
            "priority": "High",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    location = response.headers.get("location")
    assert location is not None
    assert location.startswith("/tickets/")
    detail = c.get(location)
    assert detail.status_code == 200
    assert "Cannot access virtual campus" in detail.text


def test_frontend_login_sets_cookie_and_dashboard_shows_current_user():
    c = client()

    response = c.post(
        "/login",
        data={"email": "admin@example.com", "password": "admin123"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers.get("location") == "/workspace"
    assert "helpdesk_token=" in response.headers.get("set-cookie", "")
    dashboard = c.get("/workspace")
    assert dashboard.status_code == 200
    assert "Signed in as Admin" in dashboard.text
    assert "administrator" in dashboard.text


def test_web_logout_clears_session_and_protected_pages_require_login():
    customer = client()
    customer.post("/login", data={"email": "requester@example.com", "password": "requester123"})
    assert "Customer portal" in customer.get("/portal").text
    assert 'action="/logout"' in customer.get("/portal").text

    customer_logout = customer.post("/logout", follow_redirects=False)

    assert customer_logout.status_code == 303
    assert customer_logout.headers["location"] == "/"
    assert "helpdesk_token=" in customer_logout.headers.get("set-cookie", "")
    assert customer.get("/portal", follow_redirects=False).headers["location"] == "/login"

    staff = client()
    staff.post("/login", data={"email": "technician@example.com", "password": "technician123"})
    assert 'action="/logout"' in staff.get("/workspace").text
    assert staff.post("/logout", follow_redirects=False).headers["location"] == "/"
    assert staff.get("/workspace", follow_redirects=False).headers["location"] == "/login"


def test_dashboard_catalogs_and_web_pages():
    c = client()
    admin = login(c, "admin@example.com", "admin123")
    assert c.get("/api/catalogs", headers=admin).status_code == 200
    assert "status" in c.get("/api/dashboard", headers=admin).json()
    for path in ["/login", "/", "/tickets", "/tickets/new", "/knowledge-base"]:
        response = c.get(path, follow_redirects=False)
        assert response.status_code in {200, 303}
        if response.status_code == 200:
            assert "HelpDesk EDU" in response.text


def test_notifications_are_created_for_assignment_comment_and_status_change():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    ticket_id = c.post("/api/tickets", headers=requester, json={"title": "Network is unavailable", "description": "Lab 2 cannot connect", "category": "Network", "priority": "High"}).json()["id"]

    assert c.patch(f"/api/tickets/{ticket_id}/assign", headers=technician, json={"assignee_id": 3}).status_code == 200
    assert c.post(f"/api/tickets/{ticket_id}/comments", headers=requester, json={"body": "The outage affects every workstation."}).status_code == 201
    assert c.patch(f"/api/tickets/{ticket_id}/status", headers=technician, json={"status": "In Progress"}).status_code == 200

    response = c.get("/api/notifications", headers=requester)

    assert response.status_code == 200
    assert {item["type"] for item in response.json()["items"]} >= {"status_changed"}
    assert c.get("/api/notifications", headers=technician).json()["unread_count"] >= 2


def test_ticket_close_notifies_non_actor_participant():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    ticket_id = c.post("/api/tickets", headers=requester, json={"title": "Closing notification", "description": "Confirm requester receives closure", "category": "General", "priority": "Low"}).json()["id"]

    assert c.post(f"/api/tickets/{ticket_id}/close", headers=technician).status_code == 200
    assert "closed" in {item["type"] for item in c.get("/api/notifications", headers=requester).json()["items"]}


def test_notification_read_and_list_are_owned_by_current_user():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    ticket_id = c.post("/api/tickets", headers=requester, json={"title": "Printer is offline", "description": "Library printer does not respond", "category": "Hardware", "priority": "Medium"}).json()["id"]
    c.patch(f"/api/tickets/{ticket_id}/assign", headers=technician, json={"assignee_id": 3})

    notification = c.get("/api/notifications", headers=technician).json()["items"][0]
    assert c.post(f"/api/notifications/{notification['id']}/read", headers=requester).status_code == 404
    marked = c.post(f"/api/notifications/{notification['id']}/read", headers=technician)
    assert marked.status_code == 200 and marked.json()["read_at"] is not None
    assert c.get("/api/notifications/unread-count", headers=technician).json() == {"unread_count": 0}


def test_mobile_authenticated_summary_and_compact_my_ticket_list():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    ticket = c.post("/api/tickets", headers=requester, json={"title": "Mobile ticket", "description": "Created before mobile retrieval", "category": "Software", "priority": "Low"}).json()

    summary = c.get("/api/mobile/me", headers=requester)
    listing = c.get("/api/mobile/tickets", headers=requester)

    assert summary.status_code == 200
    assert summary.json()["email"] == "requester@example.com"
    assert listing.status_code == 200
    assert listing.json()["items"] == [{"id": ticket["id"], "title": "Mobile ticket", "status": "Open", "priority": "Low", "category": "Software"}]


def test_mobile_technician_my_tickets_and_summary_are_limited_to_assigned_tickets():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    own_ticket = c.post("/api/tickets", headers=requester, json={"title": "Technician ticket", "description": "Assigned to the current technician", "category": "Hardware", "priority": "High"}).json()
    other_ticket = c.post("/api/tickets", headers=requester, json={"title": "Supervisor ticket", "description": "Assigned to another technician", "category": "Software", "priority": "Medium"}).json()
    assert c.patch(f"/api/tickets/{own_ticket['id']}/assign", headers=technician, json={"assignee_id": 3}).status_code == 200
    assert c.patch(f"/api/tickets/{other_ticket['id']}/assign", headers=technician, json={"assignee_id": 2}).status_code == 200

    listing = c.get("/api/mobile/tickets", headers=technician)
    summary = c.get("/api/mobile/me", headers=technician)

    assert listing.status_code == 200
    assert [ticket["id"] for ticket in listing.json()["items"]] == [own_ticket["id"]]
    assert summary.json()["open_ticket_count"] == 1


def test_mobile_detail_is_access_controlled_and_mobile_create_reuses_ticket_flow():
    c = client()
    requester = login(c, "requester@example.com", "requester123")
    technician = login(c, "technician@example.com", "technician123")
    created = c.post("/api/mobile/tickets", headers=requester, json={"title": "Created on mobile", "description": "Compact API creation", "category": "General", "priority": "Medium"})

    assert created.status_code == 201
    assert c.get(f"/api/mobile/tickets/{created.json()['id']}", headers=requester).status_code == 200
    assert c.get(f"/api/mobile/tickets/{created.json()['id']}", headers=technician).status_code == 200
    assert c.get("/api/mobile/me").status_code == 401


def test_local_assistance_returns_deterministic_known_network_hint():
    c = client()
    requester = login(c, "requester@example.com", "requester123")

    response = c.post("/api/assistance", headers=requester, json={"title": "Network outage", "description": "Students report that Wi-Fi cannot connect.", "category": "Network"})

    assert response.status_code == 200
    assert response.json()["matched"]
    assert "network" in response.json()["suggestions"][0]["hint"].lower()
    assert "human review" in response.json()["disclaimer"].lower()


def test_local_assistance_returns_safe_no_match_result():
    c = client()
    requester = login(c, "requester@example.com", "requester123")

    response = c.post("/api/assistance", headers=requester, json={"title": "Unusual classroom event", "description": "A completely novel situation.", "category": "Other"})

    assert response.status_code == 200
    assert not response.json()["matched"]
    assert response.json()["suggestions"] == []


def test_notifications_page_and_ticket_assistance_section_render():
    c = client()
    c.post("/login", data={"email": "technician@example.com", "password": "technician123"})

    assert "HelpDesk EDU Notifications" in c.get("/notifications").text
    assert "Local assistance suggestions" in c.get("/tickets/1").text
