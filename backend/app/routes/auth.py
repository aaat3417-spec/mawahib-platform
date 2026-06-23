from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import Role
from app.models.user import User
from app.routes.deps import get_current_user, get_db
from app.schemas.auth import OwnerSetup, Token
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for_user(user: User) -> Token:
    return Token(
        access_token=create_access_token(str(user.id), {"role": user.role}),
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/setup-owner", response_model=Token, status_code=status.HTTP_201_CREATED)
def setup_owner(payload: OwnerSetup, db: Session = Depends(get_db)) -> Token:
    if db.query(User).count() > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner setup is already complete.")
    owner = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=Role.OWNER,
        is_active=True,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return _token_for_user(owner)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive")
    return _token_for_user(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
