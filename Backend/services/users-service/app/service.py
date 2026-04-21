import uuid

from fastapi import HTTPException, status

from .models import AddSkillRequest, AddSkillResponse, CreateUserRequest, UpdateUserRequest, User, UserResponse
from .repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create_user(self, payload: CreateUserRequest) -> UserResponse:
        user = User(
            id=f"usr_{uuid.uuid4().hex[:8]}",
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        self._repository.create(user)
        return self._to_response(user)

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
        # Devolver la lista de skills como objetos con skillId y xpPoints
        return {
            "userId": user.id,
            "skills": [
                {"skillId": skill_id, "xpPoints": xp}
                for skill_id, xp in user.skills.items()
            ]
        }

    def add_skill(self, user_id: str, payload: AddSkillRequest) -> AddSkillResponse:
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        already_owned = payload.skillId in user.skills
        if already_owned:
            user.skills[payload.skillId] += payload.xpPoints
        else:
            user.skills[payload.skillId] = payload.xpPoints

        self._repository.update(user)

        return AddSkillResponse(
            userId=user.id,
            skillId=payload.skillId,
            alreadyOwned=already_owned,
            totalXP=user.skills[payload.skillId]
        )

    @staticmethod
    def _to_response(user: User) -> UserResponse:
        # Convertir el diccionario de skills a lista de UserSkill
        from .models import UserSkill
        skills_list = [UserSkill(skillId=k, xpPoints=v) for k, v in user.skills.items()]
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            skills=skills_list,
            createdAt=user.created_at,
        )
