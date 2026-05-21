import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import RequestRecord, RequestStatus, utc_now_iso


class RequestRepository:
    """
    Repositorio para persistir el estado de solicitudes del gateway.
    """
    def __init__(self) -> None:
        self._session_factory = SessionLocal

    def create_request(self, request_id: str, event_type: str, user_id: str | None, client_id: str | None) -> None:
        """Crea un registro en estado pendiente para una solicitud."""
        with self._session_factory() as session:
            session: Session
            session.add(
                RequestRecord(
                    id=request_id,
                    user_id=user_id,
                    client_id=client_id,
                    event_type=event_type,
                    status=RequestStatus.PENDING.value,
                    response_json=None,
                    error=None,
                    created_at=utc_now_iso(),
                    updated_at=utc_now_iso(),
                )
            )
            session.commit()

    def update_request(self, request_id: str, status: RequestStatus, response: Any | None, error: str | None) -> None:
        """
        Actualiza el estado y el payload de respuesta de una solicitud.
        """
        with self._session_factory() as session:
            session: Session
            record = session.get(RequestRecord, request_id)
            if not record:
                return

            record.status = status.value
            record.response_json = json.dumps(response) if response is not None else None
            record.error = error
            record.updated_at = utc_now_iso()
            session.commit()

    def get_request(self, request_id: str) -> RequestRecord | None:
        """
        Obtiene un registro de solicitud por su ID.
        """
        statement = select(RequestRecord).where(RequestRecord.id == request_id)
        with self._session_factory() as session:
            session: Session
            return session.scalars(statement).first()
