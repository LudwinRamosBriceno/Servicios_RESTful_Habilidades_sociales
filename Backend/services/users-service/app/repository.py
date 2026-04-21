from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import User
from .orm_models import UserORM


class UserRepository:
    def __init__(self) -> None:
        self._session_factory = SessionLocal

    def create(self, user: User) -> User:
        with self._session_factory() as session:
            session: Session
            session.add(
                UserORM(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    password=user.password,
                    skills=user.skills,
                    created_at=user.created_at,
                )
            )
            session.commit()
        return user

    def get_by_id(self, user_id: str) -> User | None:
        statement = select(UserORM).where(UserORM.id == user_id)
        with self._session_factory() as session:
            session: Session
            orm_user = session.scalars(statement).first()

        if not orm_user:
            return None
        return self._orm_to_user(orm_user)

    def get_by_name(self, name: str) -> User | None:
        statement = select(UserORM).where(func.lower(UserORM.name) == name.lower())
        with self._session_factory() as session:
            session: Session
            orm_user = session.scalars(statement).first()

        if not orm_user:
            return None
        return self._orm_to_user(orm_user)

    def find_all(self) -> List[User]:
        statement = select(UserORM)
        with self._session_factory() as session:
            session: Session
            orm_users = session.scalars(statement).all()

        return [self._orm_to_user(orm_user) for orm_user in orm_users]

    def update(self, user: User) -> User:
        with self._session_factory() as session:
            session: Session
            existing = session.get(UserORM, user.id)
            if not existing:
                return user

            existing.name = user.name
            existing.email = user.email
            existing.password = user.password
            existing.skills = user.skills
            existing.created_at = user.created_at
            session.commit()
        return user

    @staticmethod
    def _orm_to_user(orm_user: UserORM) -> User:
        return User(
            id=orm_user.id,
            name=orm_user.name,
            email=orm_user.email,
            password=orm_user.password,
            skills=orm_user.skills or {},
            created_at=orm_user.created_at,
        )
