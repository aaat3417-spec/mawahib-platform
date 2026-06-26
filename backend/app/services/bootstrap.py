from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.enums import Role
from app.models.team import Team
from app.models.user import User
from app.services.badges import seed_badges
from app.services.team_codes import assign_unique_team_code, ensure_team_codes

DEFAULT_TEAMS = [
    ("Programming Team", "Software, algorithms, and application development."),
    ("Research Team", "Scientific research, papers, and evidence-based exploration."),
    ("AI Team", "Machine learning, automation, and intelligent systems."),
    ("Media Team", "Creative media, publishing, and community storytelling."),
    ("Courses Team", "Learning paths, workshops, and peer teaching."),
]


def seed_defaults(db: Session) -> None:
    seed_badges(db)
    existing_team_names = {team.name for team in db.query(Team).all()}
    for name, description in DEFAULT_TEAMS:
        if name not in existing_team_names:
            team = Team(name=name, description=description)
            db.add(team)
            db.flush()
            assign_unique_team_code(db, team)

    if settings.INITIAL_OWNER_EMAIL and settings.INITIAL_OWNER_PASSWORD:
        existing_owner = db.query(User).filter(User.email == settings.INITIAL_OWNER_EMAIL).first()
        if not existing_owner:
            db.add(
                User(
                    email=settings.INITIAL_OWNER_EMAIL,
                    full_name=settings.INITIAL_OWNER_NAME,
                    hashed_password=hash_password(settings.INITIAL_OWNER_PASSWORD),
                    role=Role.OWNER,
                    is_active=True,
                )
            )
    db.commit()
    ensure_team_codes(db)
