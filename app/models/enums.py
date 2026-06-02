from enum import Enum


class ApplicationStatus(Enum):
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    GHOSTED = "ghosted"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"