from typing import Dict

from .models import User


class UserRepository:
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def update(self, user: User) -> User:
        self._users[user.id] = user
        return user
