from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.user import UserResponse

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserResponse)
def read_current_user_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user
