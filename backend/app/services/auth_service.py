from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User, UserRole
from app.schemas.auth import RegisterRequest

ALLOWED_SELF_REGISTRATION_ROLES = {
    UserRole.CITIZEN,
    UserRole.SCHOOL,
    UserRole.HEALTHCARE,
    UserRole.NGO_WORKER,
}


def register_user(db: Session, payload: RegisterRequest) -> User:
    if payload.role not in ALLOWED_SELF_REGISTRATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Government and administrator accounts must be created by an administrator.',
        )

    normalized_email = payload.email.lower().strip()
    normalized_mobile = payload.mobile_number.strip().replace(' ', '')

    existing_user = db.query(User).filter(or_(User.email == normalized_email, User.mobile_number == normalized_mobile)).first()
    if existing_user:
        if existing_user.email == normalized_email:
            raise HTTPException(status.HTTP_409_CONFLICT, detail='Email already registered.')
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Mobile number already registered.')

    user = User(
        full_name=payload.full_name.strip(),
        email=normalized_email,
        mobile_number=normalized_mobile,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        preferred_language=payload.preferred_language,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    value = identifier.strip()
    user = db.query(User).filter(or_(User.email == value.lower(), User.mobile_number == value)).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_token_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id), role=user.role.value)
