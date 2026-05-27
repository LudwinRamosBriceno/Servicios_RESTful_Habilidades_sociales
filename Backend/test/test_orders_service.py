"""Pruebas unitarias para el servicio de órdenes (OrderService)."""

import os
import sys
import unittest
from unittest.mock import patch

# Se coloca antes del import del mockup para evitar errores en los test del pre-commit
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mockups.order_mock import (
    DummyDB_CreateOrder,
)  # Es importante que este import esté en esta posición para evitar errores

# Se añade la ruta del servicio al PYTHONPATH para que los imports absolutos funcionen
service_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "services", "orders-service")
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
    "app.orm_models",
    "app.messaging",
):
    sys.modules.pop(module_name, None)

import app.service as orders_service_module

# from mockups.order_mock import DummyDB_CreateOrder
from app.models import OrderRequest, OrderResult
from app.repository import OrderRepository
from app.service import OrderService


class TestOrdersService(unittest.TestCase):
    """Pruebas unitarias para el servicio de órdenes (OrderService)."""

    def setUp(self):
        """Configura el entorno de prueba con un mock del repositorio."""

        # Se crea el repositorio y el servicio para el test de creación de orden
        repository_createOrder = OrderRepository(
            DummyDB_CreateOrder()
        )  # se le pasa la sesión de base de datos al repositorio
        self.service_createOrder = OrderService(repository=repository_createOrder)

    @patch.object(orders_service_module, "publish_event")
    def test_create_order(self, mock_publish):
        """Prueba creación de orden y publicación del evento."""

        # Solicitud de creación de orden
        order_request = OrderRequest(userId="1", productId="1", quantity=2)
        # Se crea una nueva orden o pedido (se regresa una tabla, se toma solo el objeto)
        result, _ = self.service_createOrder.create_order(
            order_request, order_request.userId, None
        )

        # se valida que la orden se haya creado correctamente
        self.assertIsInstance(
            result, OrderResult
        )  # se comprueba que el resultado sea del tipo OrderResult
        self.assertEqual(result.userId, "1")  # se comprueba el id del usuario
        self.assertEqual(result.productId, "1")  # se comprueba el id del producto


if __name__ == "__main__":
    # unittest.main()
    pass

# Ejecutar prueba: pytest Backend/test/test_orders_service.py
