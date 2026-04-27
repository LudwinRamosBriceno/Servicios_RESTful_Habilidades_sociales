from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class UserORM(Base):
    """Entidad ORM que mapea la tabla users en PostgreSQL."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    # JSON con estructura: {skill_id: skill_points}.
    skills: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Fecha de creacion en formato ISO-8601 UTC (string).
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)