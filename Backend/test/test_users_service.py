import unittest
import sys
import os

# Se añade la raíz del proyecto al PYTHONPATH para que los imports absolutos funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/users-service/app')))
from repository import UserRepository
from service import UserService
from models import CreateUserRequest
from mockups.user_mock import DummyDB_CreateUser, DummyDB_get_user_skills

class TestUserService(unittest.TestCase):
    def setUp(self):
        # Se crea el repositorio y el servicio para el test de creación de usuario
        repository_createUser = UserRepository(DummyDB_CreateUser()) # se le pasa la sesión de base de datos al repositorio
        self.service_createUser = UserService(repository=repository_createUser)

        # Se crea el repositorio y el servicio para el test de obtención de habilidades de usuario
        repository_getUserSkills = UserRepository(DummyDB_get_user_skills()) # se le pasa la sesión de base de datos al repositorio
        self.service_getUserSkills = UserService(repository=repository_getUserSkills)

    def test_create_user(self):
        user = CreateUserRequest(name="testuser", email="test@example.com", password="1234")
        response = self.service_createUser.create_user(user)
        
        # Se verifica que la prueba de creación de usuario se realizó correctamente
        self.assertEqual(response.name, "testuser")
        self.assertEqual(response.email, "test@example.com")

    def test_get_user_skills(self):
        # Se llama a get_user_skills para un usuario específico (en este caso, el usuario con ID 1)
        id_usuario = "1"
        response = self.service_getUserSkills.get_user_skills(id_usuario)

        # Se consulta que la respuesta contenga el ID del usuario y una lista de habilidades
        self.assertEqual(response["userId"], id_usuario)
        self.assertIsInstance(response["skills"], list)

if __name__ == "__main__":
    unittest.main()
