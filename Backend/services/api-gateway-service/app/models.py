from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utc_now_iso() -> str:
    """
    Devuelve fecha y hora UTC en formato ISO 8601.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class RequestStatus(str, Enum):
    """
    Estados posibles de una solicitud registrada por el gateway.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RequestRecord(Base):
    """
    Registro persistente de solicitudes y respuestas del gateway.
    """
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    client_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False, default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False, default=utc_now_iso)
