from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from pedidos.models import Producto, Pedido
from pedidos.dao.boardgamedao import PedidoDAO


class SmokeTests(TestCase):

    def setUp(self):
        """Configuración de datos iniciales para las pruebas"""

        self.producto = Producto.objects.create(
            nombre="Catan",
            precio=1500.00,
            categoria="ESTRATEGIA",
            disponible=True
        )

        self.user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='password123'
        )

    def test_creacion_producto(self):
        """Verifica que el producto se guarde correctamente en la base de datos"""

        self.assertEqual(
            Producto.objects.count(),
            1
        )

        self.assertEqual(
            self.producto.nombre,
            "Catan"
        )

    def test_creacion_pedido(self):
        """Verifica la creación de un pedido asociado a un cliente y producto"""

        pedido = Pedido.objects.create(
            cliente_nombre="Cliente Prueba",
            producto=self.producto,
            estado="RECIBIDO",
            total=self.producto.precio
        )

        self.assertEqual(
            Pedido.objects.count(),
            1
        )

        self.assertEqual(
            pedido.cliente_nombre,
            "Cliente Prueba"
        )

        self.assertEqual(
            pedido.producto,
            self.producto
        )

    def test_acceso_admin_importar_csv(self):
        """Verifica que la vista de carga masiva responda correctamente (HTTP 200)"""

        self.client.login(
            username='admin_test',
            password='password123'
        )

        response = self.client.get(
            '/admin/pedidos/producto/importar-csv/'
        )

        self.assertEqual(
            response.status_code,
            200
        )


class BoardGameHubTestCase(TestCase):

    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Catan",
            precio=899.00,
            disponible=True,
            categoria="ESTRATEGIA"
        )

    def test_crear_pedido_dao(self):
        pedido = PedidoDAO.crear_pedido_con_producto(
            "Carlos",
            self.producto.id
        )

        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.cliente_nombre, "Carlos")
        self.assertEqual(pedido.total, self.producto.precio)

    def test_cambiar_estado_dao(self):
        pedido = PedidoDAO.crear_pedido_con_producto(
            "Ana",
            self.producto.id
        )

        pedido_actualizado = PedidoDAO.cambiar_estado(
            pedido.id,
            "EN_TRANSITO"
        )

        self.assertEqual(
            pedido_actualizado.estado,
            "EN_TRANSITO"
        )

    def test_api_list_productos(self):
        """Verifica que la API de productos responda correctamente"""

        response = self.client.get('/api/productos/')

        self.assertEqual(
            response.status_code,
            200
        )

    def test_crear_pedido_action_web(self):
        response = self.client.post(
            reverse('crear_pedido'),
            {
                'cliente_nombre': 'Cliente Prueba',
                'producto_id': self.producto.id
            }
        )

        self.assertRedirects(
            response,
            reverse('catalogo')
        )

        self.assertEqual(
            Pedido.objects.count(),
            1
        )