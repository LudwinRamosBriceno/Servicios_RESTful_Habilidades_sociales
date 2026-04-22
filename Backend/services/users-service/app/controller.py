from fastapi import APIRouter

from .models import AddSkillRequest, CreateUserRequest, UpdateUserRequest, UserListItemResponse
from .repository import UserRepository
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])
# Instancia única de servicio para reutilizar la lógica de negocio en todos los endpoints.
service = UserService(UserRepository())


@router.post("")
def create_user(payload: CreateUserRequest):
    """Crea un usuario nuevo."""
    return service.create_user(payload)


@router.get("")
def list_users() -> list[UserListItemResponse]:
    """Lista los nombres e IDs de usuarios registrados."""
    return service.list_users()


@router.get("/{user_id}")
def get_user(user_id: str):
    """Obtiene el detalle de un usuario por ID."""
    return service.get_user(user_id)


@router.put("/{user_id}")
def update_user(user_id: str, payload: UpdateUserRequest):
    """Actualiza datos de un usuario existente."""
    return service.update_user(user_id, payload)


@router.get("/{user_id}/skills")
def get_user_skills(user_id: str):
    """Devuelve las habilidades del usuario con su puntaje."""
    return service.get_user_skills(user_id)


@router.put("/{user_id}/skills")
def add_user_skill(user_id: str, payload: AddSkillRequest):
    """Agrega una habilidad al usuario o suma puntos si ya la tiene."""
    return service.add_skill(user_id, payload)
