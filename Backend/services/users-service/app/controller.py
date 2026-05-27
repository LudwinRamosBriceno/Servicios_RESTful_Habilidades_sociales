"""Controlador de FastAPI para manejar rutas relacionadas con usuarios."""

from fastapi import APIRouter

from .db import SessionLocal
from .models import (
    AddSkillRequest,
    AuthenticateUserRequest,
    CreateUserRequest,
    UpdateUserRequest,
    UserListItemResponse,
)
from .repository import UserRepository
from .service import UserService

# Enrutador de FastAPI para manejar las rutas relacionadas con los usuarios.
router = APIRouter(prefix="/users", tags=["users"])

# Inicialización del servicio de usuarios con su repositorio.
repository = UserRepository(
    SessionLocal
)  # se le pasa la sesión de base de datos al repositorio
service = UserService(repository=repository)


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
    """Agrega una habilidad o suma puntos si ya existe."""
    return service.add_skill(user_id, payload)


@router.post("/auth/verify")
def verify_credentials(payload: AuthenticateUserRequest):
    """Valida credenciales para uso interno de auth-service."""
    return service.authenticate_user(payload)
