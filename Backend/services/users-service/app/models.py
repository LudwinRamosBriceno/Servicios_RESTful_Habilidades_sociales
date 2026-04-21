from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, EmailStr, Field


def utc_now_iso() -> str:
    """Genera fecha/hora UTC en formato ISO-8601 sin microsegundos."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class UserSkill(BaseModel):
    """Representa una habilidad con su nombre y puntaje del usuario."""
    skillId: str
    skillName: str
    skillPoints: int = 0


class User(BaseModel):
    """Modelo interno de usuario almacenado en el servicio."""
    id: str
    name: str
    email: EmailStr
    password: str
    # Mapa: id de habilidad -> puntos acumulados.
    skills: Dict[str, int] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)


class CreateUserRequest(BaseModel):
    """Payload para crear un usuario."""
    name: str
    email: EmailStr
    password: str


class UpdateUserRequest(BaseModel):
    """Payload para actualización parcial de un usuario."""
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class AddSkillRequest(BaseModel):
    """Payload para agregar una habilidad y sus puntos a un usuario."""
    skillId: str
    skillPoints: int


class UserResponse(BaseModel):
    """Respuesta completa del usuario para la API."""
    id: str
    name: str
    email: EmailStr
    skills: List[UserSkill]
    createdAt: str


class UserNameResponse(BaseModel):
    """Respuesta liviana con solo el nombre del usuario."""
    name: str


class AddSkillResponse(BaseModel):
    """Respuesta de la operación de alta/acumulación de habilidad."""
    userId: str
    skillId: str
    alreadyOwned: bool
    skillPoints: int
