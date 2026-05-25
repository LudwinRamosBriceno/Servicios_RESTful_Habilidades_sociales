
class DummyOrderORM:
    def __init__(self, id, user_id, product_id, quantity):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity


class DummyDB_CreateOrder:
    def __init__(self):
        self.orders = []
       
    def add(self, order_orm):
        self.orders.append(DummyOrderORM(
            id=order_orm.id,
            user_id=order_orm.user_id,
            product_id=order_orm.product_id,
            quantity=order_orm.quantity
        ))

    def commit(self):
        return True

    # Métodos para simular el contexto de sesión (si no se coloca se obtiene error al usar "with")
    def __call__(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass