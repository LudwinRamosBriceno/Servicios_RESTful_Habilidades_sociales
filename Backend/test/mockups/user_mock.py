"""Mockups para pruebas unitarias relacionadas con usuarios."""


class DummyUser:
    """Representa un usuario de prueba con atributos predefinidos."""

    def __init__(self):
        """Inicializa un usuario de prueba con datos predefinidos."""
        self.id = "1"
        self.name = "testuser"
        self.email = "test@example.com"
        self.password = "1234"
        self.skills = {"comunicacion": 10, "liderazgo": 8}
        self.created_at = "2024-01-01"


class DummyDB_CreateUser:
    """Simula una base de datos para la creación de usuarios."""

    def __init__(self):
        """Inicializa la base de datos simulada con usuarios vacíos."""
        self.users = {}
        self.committed = False
        self.user = None  # Si se coloca DummyUser() se simula que el usuario ya existe, y el test falla

    def add(self, user_orm):
        """Simula la adición de un nuevo usuario a la base de datos."""
        self.users[user_orm.id] = user_orm

    def commit(self):
        """Simula la confirmación de cambios en la base de datos."""
        self.committed = True

    def scalars(self, statement):
        """Simula la consulta de un usuario por nombre o email."""

        class ScalarResult:
            """Simula el resultado de una consulta de usuario."""

            def __init__(self, user):
                self._user = user

            def first(self):
                # Se retorna un usuario
                return self._user

        return ScalarResult(self.user)

    # Métodos para simular el contexto de sesión (si no se coloca se obtiene error al usar "with")
    def __call__(self):
        """Permite usar la clase como contexto de sesión."""
        return self

    def __enter__(self):
        """Entra al contexto de sesión."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sale del contexto de sesión."""
        pass


# Dummy para simular la DB en el método get_user_skills del repositorio
class DummyDB_get_user_skills:
    """Simula la base de datos para obtener skills de usuario."""

    def __init__(self):
        """Inicializa el usuario de prueba con skills."""
        # Simula un usuario con skills
        self.user = DummyUser()

    # Simula la consulta de skills por ID de usuario
    def scalars(self, statement):
        """Simula la consulta de skills por ID de usuario."""

        class ScalarResult:
            """Simula el resultado de una consulta de skills por ID de usuario."""

            def __init__(self, user):
                self._user = user

            def first(self):
                return self._user

            def all(self):
                return [self._user]

        return ScalarResult(self.user)

    def get(self, orm_class, user_id):
        """Simula la búsqueda de usuario por ID."""
        return self.user if user_id == self.user.id else None

    # Métodos para simular el contexto de sesión (si no se coloca se obtiene error al usar "with")
    def __call__(self):
        """Permite usar la clase como contexto de sesión."""
        return self

    def __enter__(self):
        """Entra al contexto de sesión."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sale del contexto de sesión."""
        pass
