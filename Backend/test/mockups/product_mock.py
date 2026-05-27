"""Mockups para pruebas unitarias de productos."""


class Dummy_orm_Product:
    """Mockup de producto para pruebas."""

    def __init__(self, id, name, description, stock, active):
        """Inicializa el producto de prueba con sus atributos."""
        self.id = id
        self.name = name
        self.description = description
        self.stock = stock
        self.active = active


class DummyDB_get_products:
    """Mockup de base de datos para listar productos."""

    def __init__(self):
        """Inicializa la lista de productos de prueba."""
        # Lista de productos de prueba
        self.products = [
            Dummy_orm_Product(
                id="1",
                name="Producto A",
                description="Descripción del Producto A",
                stock=5,
                active=True,
            ),
            Dummy_orm_Product(
                id="2",
                name="Producto B",
                description="Descripción del Producto B",
                stock=0,
                active=True,
            ),
        ]

    def scalars(self, statement):
        """Simula el resultado de una consulta de productos."""

        class Result:
            def __init__(self, products):
                self._products = products

            def all(self):
                return self._products  # se regresa la lista de todos los productos

        return Result(self.products)

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


class DummyDB_CreateProduct:
    """Mockup de base de datos para crear productos."""

    def __init__(self):
        """Inicializa la lista de productos de prueba."""
        # Lista de productos de prueba
        self.products = [
            Dummy_orm_Product(
                id="1",
                name="Producto A",
                description="Descripción del Producto A",
                stock=5,
                active=True,
            ),
            Dummy_orm_Product(
                id="2",
                name="Producto B",
                description="Descripción del Producto B",
                stock=0,
                active=True,
            ),
        ]

    # Simula la obtención de la lista de todos los productos disponibles
    def get(self, orm_class, product_id):
        """Simula la obtención de un producto por ID."""
        for product in self.products:
            if product.id == product_id:
                return product
        return None

    # Simula la adición de un nuevo producto a la base de datos
    def add(self, product_orm):
        """Simula la adición de un producto a la base de datos."""
        # Se agrega el nuevo producto
        self.products.append(
            Dummy_orm_Product(
                id=product_orm.id,
                name=product_orm.name,
                description=product_orm.description,
                stock=product_orm.stock,
                active=product_orm.active,
            )
        )
        return True

    def commit(self):
        """Simula el commit en la base de datos."""
        return True

    def scalars(self, statement):
        """Simula el resultado de una consulta de productos."""

        class Result:
            def __init__(self, products):
                self._products = products

            def all(self):
                return self._products

        return Result(self.products)

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
