"""Pruebas unitarias para el servicio de autenticación (AuthService)."""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

# Se añade la ruta del servicio al PYTHONPATH para que los imports absolutos funcionen
service_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "services", "auth-service")
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
    "app",
    "app.models",
    "app.repository",
    "app.service",
    "app.clients",
    "app.clients.user_http_client",
):
    sys.modules.pop(module_name, None)

from app.models import LoginRequest
from app.repository import AuthRepository
from app.service import AuthService
from app.session_store import create_session


class TestAuthService(unittest.TestCase):
    """Pruebas unitarias para el servicio de autenticación (AuthService)."""

    def setUp(self):
        """Configura mocks del cliente HTTP y el repositorio de autenticación."""

        # Crea un mock del UserHttpClient (cliente HTTP)
        mock_client = MagicMock()
        fake_user = SimpleNamespace(user_id="1", name="testuser")
        mock_client.verify_credentials.return_value = fake_user

        # Se crea el repositorio y el servicio para el test de login
        repository_login = AuthRepository(
            mock_client
        )  # se le pasa el mock del cliente HTTP al repositorio
        self.service_login = AuthService(repository_login)

    def test_login(self):
        """Prueba login verificando credenciales y creación de sesión."""

        # simula un login con credenciales de prueba
        request_user = LoginRequest(
            email="test@example.com", password="1234"
        )  # Objeto de solicitud de login

        # se comprueban los datos del inicio de sesión con un mock del cliente HTTP
        user_result = self.service_login.login(request_user)

        # se crea una sesión para el usuario autenticado
        session_id = create_session(user_result.user_id, user_result.name)

        # se compruebra que se haya generado un ID de sesión
        self.assertIsNotNone(session_id)


if __name__ == "__main__":
    # unittest.main()
    pass
# Ejecutar prueba: pytest Backend/test/test_auth_service.py
