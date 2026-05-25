
import unittest
import sys
import os
from unittest.mock import patch

# Se añade la raíz del proyecto al PYTHONPATH para que los imports absolutos funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/orders-service/app')))
from repository import OrderRepository
from service import OrderService
from models import OrderRequest, OrderResult
from mockups.order_mock import DummyDB_CreateOrder


class TestOrdersService(unittest.TestCase):

    def setUp(self):
        # Se crea el repositorio y el servicio para el test de creación de orden
        repository_createOrder = OrderRepository(DummyDB_CreateOrder()) # se le pasa la sesión de base de datos al repositorio
        self.service_createOrder = OrderService(repository=repository_createOrder)

    @patch('service.publish_event')
    def test_create_order(self, mock_publish):
        # Solicitud de creación de orden
        order_request = OrderRequest(
            userId="1",
            productId="1",
            quantity=2
        )
        # Se crea una nueva orden o pedido (se regresa una tabla, se toma solo el objeto)
        result,_ = self.service_createOrder.create_order(order_request, order_request.userId, None)

        # se valida que la orden se haya creado correctamente
        self.assertIsInstance(result, OrderResult) # se comprueba que el resultado sea del tipo OrderResult
        self.assertEqual(result.userId, "1") # se comprueba el id del usuario
        self.assertEqual(result.productId, "1") # se comprueba el id del producto

if __name__ == '__main__':
    pass
