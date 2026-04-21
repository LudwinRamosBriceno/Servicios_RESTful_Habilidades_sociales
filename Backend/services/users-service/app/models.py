from datetime import datetime, timezone
from typing import List, Dict

from pydantic import BaseModel, EmailStr, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



class UserSkill(BaseModel):
    skillId: str
    xpPoints: int = 0


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    password: str
    skills: Dict[str, int] = {}
    created_at: str = Field(default_factory=utc_now_iso)


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class AddSkillRequest(BaseModel):
    skillId: str
    xpPoints: int


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    skills: List[UserSkill]
    createdAt: str


class AddSkillResponse(BaseModel):
    userId: str
    skillId: str
    alreadyOwned: bool
    totalXP: int
