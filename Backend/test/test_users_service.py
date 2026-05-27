"""Pruebas unitarias para el servicio de usuarios (UserService)."""

import importlib
import os
import sys
import unittest

# Se coloca antes del import del mockup para evitar errores en los test del pre-commit
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mockups.user_mock import (  # Es importante que estos imports estén en esta posición para evitar errores
    DummyDB_CreateUser,
    DummyDB_get_user_skills,
)

# Se añade la ruta del servicio al PYTHONPATH para que los imports absolutos funcionen
service_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "services", "users-service", "app")
)
sys.path.insert(0, service_path)

# Elimina rutas de otros servicios para evitar conflictos de imports (esto porque las carpetas de servicios tiene guiones)
services_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "services")
)
normalized_service_path = os.path.normcase(service_path)
for path in list(sys.path):
    normalized_path = os.path.normcase(os.path.abspath(path))
    if (
        normalized_path.startswith(os.path.normcase(services_root))
        and normalized_path != normalized_service_path
    ):
        sys.path.remove(path)

# Evita reutilizar modulos cacheados con el mismo nombre de otros servicios.
for module_name in (
    "models",
    "repository",
    "service",
    "orm_models",
    "clients",
    "clients.product_http_client",
):
    sys.modules.pop(module_name, None)

users_models = importlib.import_module("models")

# from mockups.user_mock import DummyDB_CreateUser, DummyDB_get_user_skills
from models import CreateUserRequest
from repository import UserRepository
from service import UserService


class TestUserService(unittest.TestCase):
    """Pruebas unitarias para el servicio de usuarios (UserService)."""

    def setUp(self):
        """Configura mocks del repositorio para pruebas de usuarios."""

        # Refuerza el modulo correcto para imports diferidos dentro del servicio.
        sys.modules["models"] = users_models

        # Se crea el repositorio y el servicio para el test de creación de usuario
        repository_createUser = UserRepository(
            DummyDB_CreateUser()
        )  # se le pasa la sesión de base de datos al repositorio
        self.service_createUser = UserService(repository=repository_createUser)

        # Se crea el repositorio y el servicio para el test de obtención de habilidades de usuario
        repository_getUserSkills = UserRepository(
            DummyDB_get_user_skills()
        )  # se le pasa la sesión de base de datos al repositorio
        self.service_getUserSkills = UserService(repository=repository_getUserSkills)

    def test_create_user(self):
        """Prueba la creación de un nuevo usuario."""

        user = CreateUserRequest(
            name="testuser", email="test@example.com", password="1234"
        )
        response = self.service_createUser.create_user(user)

        # Se verifica que la prueba de creación de usuario se realizó correctamente
        self.assertEqual(response.name, "testuser")
        self.assertEqual(response.email, "test@example.com")

    def test_get_user_skills(self):
        """Prueba la obtención de habilidades de un usuario específico."""

        # Se llama a get_user_skills para un usuario específico (en este caso, el usuario con ID 1)
        id_usuario = "1"
        response = self.service_getUserSkills.get_user_skills(id_usuario)

        # Se consulta que la respuesta contenga el ID del usuario y una lista de habilidades
        self.assertEqual(response["userId"], id_usuario)
        self.assertIsInstance(response["skills"], list)


if __name__ == "__main__":
    # unittest.main()
    pass

# Ejecutar prueba: pytest Backend/test/test_users_service.py
