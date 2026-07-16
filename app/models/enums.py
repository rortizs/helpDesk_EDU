"""Domain vocabulary kept in one place for classroom discussion."""
from enum import StrEnum


class Role(StrEnum):
    ADMINISTRATOR = "administrator"
    SUPERVISOR = "supervisor"
    TECHNICIAN = "technician"
    REQUESTER = "requester"


class TicketStatus(StrEnum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


CATEGORIES = ["General", "Hardware", "Software", "Network"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = [status.value for status in TicketStatus]
