
# Dummy para simular usuarios en la base de datos
class DummyUser:
    def __init__(self):
        self.id = "1"
        self.name = "testuser"
        self.email = "test@example.com"
        self.password = "1234"
        self.skills = {"comunicacion": 10, "liderazgo": 8}
        self.created_at = "2024-01-01"


# Dummy para simular la DB en el método create del repositorio
class DummyDB_CreateUser:
    def __init__(self):
        self.users = {}
        self.committed = False
        self.user = None # Si se coloca DummyUser() se simula que el usuario ya existe, y el test falla
        
    def add(self, user_orm):
        self.users[user_orm.id] = user_orm
    def commit(self):
        self.committed = True

    def scalars(self, statement):
        # Simula select por nombre
        class ScalarResult:
            def __init__(self, user):
                self._user = user
            def first(self):
                # Se retorna un usuario
                return self._user
        return ScalarResult(self.user)
    
    # Métodos para simular el contexto de sesión (si no se coloca se obtiene error al usar "with")
    def __call__(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Dummy para simular la DB en el método get_user_skills del repositorio
class DummyDB_get_user_skills:
    def __init__(self):
        # Simula un usuario con skills
        self.user = DummyUser()
    
    # Simula la consulta de skills por ID de usuario
    def scalars(self, statement):
        class ScalarResult:
            def __init__(self, user):
                self._user = user
            def first(self):
                return self._user
            def all(self):
                return [self._user]
        return ScalarResult(self.user)
    
    def get(self, orm_class, user_id):
        return self.user if user_id == self.user.id else None
    
    # Métodos para simular el contexto de sesión (si no se coloca se obtiene error al usar "with")
    def __call__(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
