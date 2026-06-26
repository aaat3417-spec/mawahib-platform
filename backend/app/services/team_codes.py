import secrets
import string

from sqlalchemy.orm import Session

from app.models.team import Team

CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_team_code(length: int = 8) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


def assign_unique_team_code(db: Session, team: Team) -> str:
    for _ in range(20):
        code = generate_team_code()
        exists = db.query(Team).filter(Team.team_code == code, Team.id != team.id).first()
        if not exists:
            team.team_code = code
            team.is_code_active = True
            return code
    raise RuntimeError("Could not generate a unique team code.")


def ensure_team_codes(db: Session) -> None:
    changed = False
    for team in db.query(Team).filter(Team.team_code.is_(None)).all():
        assign_unique_team_code(db, team)
        changed = True
    if changed:
        db.commit()
