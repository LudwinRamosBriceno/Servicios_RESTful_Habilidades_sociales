import unittest
import sys
import os

# Se añade la raíz del proyecto al PYTHONPATH para que los imports absolutos funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/products-service/app')))
from repository import ProductRepository
from service import ProductService
from models import CreateProductRequest
from mockups.product_mock import DummyDB_get_products, DummyDB_CreateProduct

class TestProductsService(unittest.TestCase):
    def setUp(self):
        # Se crea el repositorio y el servicio para el test de obtención de productos
        repository_getProducts = ProductRepository(DummyDB_get_products()) # se le pasa la sesión de base de datos al repositorio
        self.service_getProducts = ProductService(repository=repository_getProducts)

        # Se crea el repositorio y el servicio para el test de creación de productos
        repository_createProduct = ProductRepository(DummyDB_CreateProduct()) # se le pasa la sesión de base de datos al repositorio
        self.service_createProduct = ProductService(repository=repository_createProduct)

    def test_get_all_products_in_stock(self):
        result = self.service_getProducts.list_products() # se recibe una lista de objetos ProductResponse
        self.assertEqual(result[0].name, 'Producto A')

    def test_create_new_product(self):
        new_product = CreateProductRequest(
            name='Producto C', 
            description='Descripción del Producto C', 
            stock=7,
            active=True
        )
        # Se inserta un nuevo producto 
        self.service_createProduct.create_product(new_product) # se recibe un objeto ProductResponse

        # Se obtiene la lista de productos para verificar que el nuevo producto se haya agregado
        result = self.service_createProduct.list_products() # se recibe una lista de todos los productos disponibles (tipo ProductResponse)
        index_nuevo_producto = len(result) - 1 
        self.assertEqual(result[index_nuevo_producto].name, 'Producto C')

if __name__ == '__main__':
    pass

# Ejecutar prueba: pytest Backend/test/test_products_service.py