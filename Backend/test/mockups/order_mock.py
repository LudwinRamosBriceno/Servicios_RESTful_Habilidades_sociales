"""Mockups para pruebas unitarias de ordenes."""


class DummyOrderORM:
    """Mockup para representar un objeto de orden en la base de datos."""

    def __init__(self, id, user_id, product_id, quantity):
        """Inicializa una instancia con los atributos necesarios."""
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity


class DummyDB_CreateOrder:
    """Mockup para simular la base de datos del repositorio de órdenes."""

    def __init__(self):
        """Inicializa el mockup con una lista vacía de órdenes."""
        self.orders = []

    def add(self, order_orm):
        """Simula la adición de una nueva orden a la base de datos."""
        self.orders.append(
            DummyOrderORM(
                id=order_orm.id,
                user_id=order_orm.user_id,
                product_id=order_orm.product_id,
                quantity=order_orm.quantity,
            )
        )

    def commit(self):
        """Simula la confirmación de los cambios en la base de datos."""
        return True

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
