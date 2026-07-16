"""Deterministic, local-only troubleshooting hint matching."""
from app.schemas.assistance import AssistanceIn


class AssistanceService:
    DISCLAIMER = "Local deterministic suggestions only; no ticket data is transmitted externally. Human review is required before acting."
    RULES = (
        ("network", ("network", "wifi", "wi-fi", "internet", "connect"), "Check the network cable or access point, confirm the device has a valid IP address, then retry the connection."),
        ("hardware", ("printer", "projector", "keyboard", "mouse", "offline"), "Check power and physical connections, then verify the device is selected and available in the operating system."),
        ("software", ("software", "application", "app", "login", "password"), "Confirm the application version and account permissions, then reproduce the issue with the documented steps."),
    )

    def suggest(self, request: AssistanceIn) -> dict:
        text = f"{request.title} {request.description} {request.category}".lower()
        suggestions = [{"topic": topic, "hint": hint} for topic, keywords, hint in self.RULES if any(keyword in text for keyword in keywords)]
        return {"matched": bool(suggestions), "suggestions": suggestions, "disclaimer": self.DISCLAIMER}