import uuid
import os

from fastapi import HTTPException, status

from .models import AddSkillRequest, AddSkillResponse, CreateUserRequest, UpdateUserRequest, User, UserNameResponse, UserResponse
from .repository import UserRepository
from .clients.product_http_client import ProductHttpClient


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository
        products_service_url = os.getenv("PRODUCTS_SERVICE_URL", "http://products-service:8002")
        self._product_client = ProductHttpClient(products_service_url)

    def create_user(self, payload: CreateUserRequest) -> UserResponse:
        existing_user = self._repository.get_by_name(payload.name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User name already exists",
            )

        user = User(
            id=f"usr_{uuid.uuid4().hex[:8]}",
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        self._repository.create(user)
        return self._to_response(user)
    
    def list_users(self) -> list[UserNameResponse]:
        users = self._repository.find_all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
        return [UserNameResponse(name=user.name) for user in users]

    def get_user(self, user_id: str) -> UserResponse:
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self._to_response(user)

    def update_user(self, user_id: str, payload: UpdateUserRequest) -> UserResponse:
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if payload.name is not None:
            existing_user = self._repository.get_by_name(payload.name)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User name already exists",
                )
            user.name = payload.name
        if payload.email is not None:
            user.email = payload.email
        if payload.password is not None:
            user.password = payload.password

        self._repository.update(user)
        return self._to_response(user)

    def get_user_skills(self, user_id: str) -> dict:
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # Enriquecer skills con nombre para facilitar visualizacion en el cliente.
        return {
            "userId": user.id,
            "skills": [
                {
                    "skillId": skill_id,
                    "skillName": self._resolve_skill_name(skill_id),
                    "skillPoints": points,
                }
                for skill_id, points in user.skills.items()
            ]
        }

    def add_skill(self, user_id: str, payload: AddSkillRequest) -> AddSkillResponse:
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        already_owned = payload.skillId in user.skills
        if already_owned:
            user.skills[payload.skillId] += payload.skillPoints
        else:
            user.skills[payload.skillId] = payload.skillPoints

        self._repository.update(user)

        return AddSkillResponse(
            userId=user.id,
            skillId=payload.skillId,
            alreadyOwned=already_owned,
            skillPoints=user.skills[payload.skillId]
        )

    def _to_response(self, user: User) -> UserResponse:
        from .models import UserSkill
        skills_list = [
            UserSkill(skillId=skill_id, skillName=self._resolve_skill_name(skill_id), skillPoints=points)
            for skill_id, points in user.skills.items()
        ]
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            skills=skills_list,
            createdAt=user.created_at,
        )

    def _resolve_skill_name(self, skill_id: str) -> str:
        skill_name = self._product_client.get_product_name(skill_id)
        return skill_name if skill_name else "Unknown skill"
