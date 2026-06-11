import uuid
import os

from fastapi import HTTPException, status

from .models import AddSkillRequest, AddSkillResponse, CreateUserRequest, UpdateUserRequest, User, UserListItemResponse, UserResponse
from .repository import UserRepository
from .clients.product_http_client import ProductHttpClient


class UserService:
    """Servicio para gestionar usuarios y sus habilidades."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository
        # URL configurable para poder cambiar entre entornos local/docker/k8s.
        products_service_url = os.getenv("PRODUCTS_SERVICE_URL", "http://products-service:8002")
        self._product_client = ProductHttpClient(products_service_url)

    def create_user(self, payload: CreateUserRequest) -> UserResponse:
        """Crea un usuario validando que el nombre no exista previamente."""
        existing_user = self._repository.get_by_name(payload.name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya existe",
            )

        # ID corto con prefijo funcional para facilitar trazabilidad en logs.
        user = User(
            id=f"usr_{uuid.uuid4().hex[:8]}",
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        self._repository.create(user)
        return self._to_response(user)
    
    def list_users(self) -> list[UserListItemResponse]:
        """Lista de todos los usuarios."""
        users = self._repository.find_all()
        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay usuarios registrados")
        return [UserListItemResponse(id=user.id, name=user.name) for user in users]

    def get_user(self, user_id: str) -> UserResponse:
        """Obtiene un usuario por su ID."""
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return self._to_response(user)

    def update_user(self, user_id: str, payload: UpdateUserRequest) -> UserResponse:
        """Actualiza campos del usuario de forma parcial (solo si llegan en payload)."""
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        if payload.name is not None:
            # Evita colisiones de nombre con otros usuarios.
            existing_user = self._repository.get_by_name(payload.name)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El nombre de usuario ya existe",
                )
            user.name = payload.name
        if payload.email is not None:
            user.email = payload.email
        if payload.password is not None:
            user.password = payload.password

        self._repository.update(user)
        return self._to_response(user)

    def get_user_skills(self, user_id: str) -> dict:
        """Devuelve las habilidades del usuario con nombre legible."""
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        # Skills con nombre para facilitar visualizacion en el cliente.
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
        """Agrega una habilidad o acumula puntos si ya existe en el usuario."""
        user = self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

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
        """Mapea el modelo interno a DTO de respuesta para la API."""
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
        """Busca el nombre en products-service y, si no existe, devuelve 'Skill desconocida'."""
        skill_name = self._product_client.get_product_name(skill_id)
        return skill_name if skill_name else "Skill desconocida"
