from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib import messages
from rest_framework import status

from pedidos.dao.boardgamedao import ProductoDAO, PedidoDAO
from pedidos.serializers import ProductoSerializer, PedidoSerializer

# ==========================================
# ROLES
# ==========================================

def es_gestor_pedidos(user):
    """Verifica si el usuario autenticado pertenece al grupo 'Pedidos' o es Staff/Admin"""
    return user.is_authenticated and (
        user.groups.filter(name='Pedidos').exists() or user.is_staff
    )


# ==========================================
# 1. VISTAS WEB (HTML)
# ==========================================

def catalogo_view(request):
    """Muestra el catálogo de juegos de mesa utilizando el DAO"""
    productos = ProductoDAO.obtener_disponibles()

    return render(
        request,
        'mainvista/catalogo.html',
        {'productos': productos}
    )

@login_required # type: ignore
@user_passes_test(es_gestor_pedidos, login_url='/admin/login/') # type: ignore
def catalogo_view(request):
    """Muestra las comandas al Barista/Cocina utilizando el DAO"""
    # Consulta solo comandas activas con el nuevo metodo del DAO
    pedidos_activos = PedidoDAO.obtener_pendientes_o_en_preparacion()
    return render(request, 'mainvista/pedidos.html', {'pedidos': pedidos_activos})

def crear_pedido_action(request):
    """Procesa el formulario web de un nuevo pedido"""
    if request.method == 'POST':
        cliente_nombre = request.POST.get('cliente_nombre', '').strip()
        producto_id = request.POST.get('producto_id')

        if cliente_nombre and producto_id:
            pedido = PedidoDAO.crear_pedido_con_producto(cliente_nombre, int(producto_id))
            if pedido:
                messages.success(request, f"¡Pedido registrado a nombre de {cliente_nombre}!")
            else:
                messages.error(request, "Ocurrió un problema al registrar el producto.")
        else:
            messages.error(request, "Por favor ingresa tu nombre para procesar el pedido.")

    return redirect('pedidos') # <-- CAMBIAR A 'menu'

@login_required
@user_passes_test(es_gestor_pedidos, login_url='/admin/login/')
def cambiar_estado_action(request, pedido_id):
    """Actualiza el estado de una comanda desde la vista web"""
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        PedidoDAO.cambiar_estado(pedido_id, nuevo_estado)
    return redirect('catalogo')



# ==========================================
# 2. VISTAS API REST (JSON)
# ==========================================

class ProductoViewSet(viewsets.ViewSet):

    def list(self, request):
        productos = ProductoDAO.obtener_todos()
        serializer = ProductoSerializer(productos, many=True)

        return Response(serializer.data)

class PedidoViewSet(viewsets.ViewSet):
    # Permite listar los pedidos (GET)
    def list(self, request):
        pedidos = PedidoDAO.obtener_todos()
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    # Permite crear un pedido desde la API (POST)
    def create(self, request):
        cliente_nombre = request.data.get('cliente_nombre')
        producto_id = request.data.get('producto_id')

        if not cliente_nombre or not producto_id:
            return Response(
                {"error": "Se requieren cliente_nombre y producto_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido = PedidoDAO.crear_pedido_con_producto(cliente_nombre, int(producto_id))
        if pedido:
            serializer = PedidoSerializer(pedido)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Producto no encontrado o no disponible"},
            status=status.HTTP_404_NOT_FOUND
        )