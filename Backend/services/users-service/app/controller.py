from fastapi import APIRouter

from .models import AddSkillRequest, CreateUserRequest, UpdateUserRequest, UserListItemResponse
from .repository import UserRepository
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService(UserRepository())


@router.post("")
def create_user(payload: CreateUserRequest):
    return service.create_user(payload)

@router.get("")
def list_users() -> list[UserListItemResponse]:
    return service.list_users()

@router.get("/{user_id}")
def get_user(user_id: str):
    return service.get_user(user_id)

@router.put("/{user_id}")
def update_user(user_id: str, payload: UpdateUserRequest):
    return service.update_user(user_id, payload)


@router.get("/{user_id}/skills")
def get_user_skills(user_id: str):
    return service.get_user_skills(user_id)


@router.put("/{user_id}/skills")
def add_user_skill(user_id: str, payload: AddSkillRequest):
    return service.add_skill(user_id, payload)
