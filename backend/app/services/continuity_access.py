from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.continuity_models import Child, Family, FamilyAccess
from app.db.models import User


def ensure_family_access(
    db: Session,
    user: User,
    family_id: UUID,
    allowed_roles: tuple[str, ...],
    allow_grant: bool = True,
) -> Family:
    if user.role.value not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Your role cannot access this information.')
    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Family not found.')
    if user.role.value == 'ADMIN' or family.primary_guardian_user_id == user.id:
        return family
    if allow_grant:
        grant = (
            db.query(FamilyAccess)
            .filter(
                FamilyAccess.family_id == family_id,
                FamilyAccess.user_id == user.id,
                FamilyAccess.access_role == user.role.value,
            )
            .first()
        )
        if grant:
            return family
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized for this family.')


def ensure_child_access(
    db: Session,
    user: User,
    child_id: UUID,
    allowed_roles: tuple[str, ...],
) -> Child:
    child = db.get(Child, child_id)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Child not found.')
    ensure_family_access(db, user, child.family_id, allowed_roles)
    return child