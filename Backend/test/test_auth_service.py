from types import SimpleNamespace
import unittest
import sys
import os
from unittest.mock import MagicMock
from urllib import request

# Se añade la raíz del proyecto al PYTHONPATH para que los imports absolutos funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/auth-service/app')))
from repository import AuthRepository
from service import AuthService
from models import LoginRequest


class TestAuthService(unittest.TestCase):
    def setUp(self):
        # Crea un mock del UserHttpClient
        mock_client = MagicMock()
        fake_user = SimpleNamespace(user_id="1", name="testuser")
        mock_client.verify_credentials.return_value = fake_user

        # Se crea el repositorio y el servicio para el test de login
        repository_login = AuthRepository(mock_client) # se le pasa el mock del cliente HTTP al repositorio
        self.service_login = AuthService(repository_login)

    def test_login(self):
        # Simula un login con credenciales de prueba
        request_user = LoginRequest(email="test@example.com", password="1234")
        result = self.service_login.login(request_user)

        # Se verifica que el token de acceso se haya generado correctamente
        self.assertIsNotNone(result.access_token)

if __name__ == '__main__':
    pass
# Ejecutar prueba: pytest Backend/test/test_auth_service.py
