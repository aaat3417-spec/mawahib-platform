from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    TEAM_LEADER = "team_leader"
    STUDENT = "student"


class TaskCategory(StrEnum):
    PROGRAMMING = "Programming"
    RESEARCH = "Research"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    ENGLISH = "English"
    INNOVATION = "Innovation"


class TaskDifficulty(StrEnum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class SubmissionStatus(StrEnum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    NEEDS_REVISION = "Needs Revision"
    REJECTED = "Rejected"


class PointReason(StrEnum):
    TASK_COMPLETION = "task_completion"
    EXCELLENT_WORK = "excellent_work"
    EXTRA_TASK = "extra_task"
    HELPING_MEMBERS = "helping_members"
    LATE_SUBMISSION = "late_submission"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class BadgeCode(StrEnum):
    RESEARCHER = "researcher"
    PROGRAMMER = "programmer"
    AI_EXPERT = "ai_expert"
    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    TOP_STUDENT = "top_student"


class NotificationType(StrEnum):
    NEW_TASK = "new_task"
    SUBMISSION_ACCEPTED = "submission_accepted"
    SUBMISSION_REJECTED = "submission_rejected"
    NEW_ANNOUNCEMENT = "new_announcement"
    BADGE_EARNED = "badge_earned"
    RANK_CHANGED = "rank_changed"

