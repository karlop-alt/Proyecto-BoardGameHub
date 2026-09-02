from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import viewsets
from rest_framework.response import Response

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


@login_required
@user_passes_test(es_gestor_pedidos, login_url='/admin/login/')
def pedidos_view(request):
    """Muestra los pedidos registrados utilizando el DAO"""
    pedidos = PedidoDAO.obtener_todos()

    return render(
        request,
        'mainvista/pedidos.html',
        {'pedidos': pedidos}
    )


def crear_pedido_action(request):
    """Procesa el formulario web de un nuevo pedido"""
    if request.method == 'POST':
        cliente_nombre = request.POST.get('cliente_nombre')
        producto_id = request.POST.get('producto_id')

        PedidoDAO.crear_pedido_con_producto(
            cliente_nombre,
            producto_id
        )

    return redirect('pedidos')


@login_required
@user_passes_test(es_gestor_pedidos, login_url='/admin/login/')
def cambiar_estado_action(request, pedido_id):
    """Actualiza el estado de un pedido desde la vista web"""
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')

        PedidoDAO.cambiar_estado(
            pedido_id,
            nuevo_estado
        )

    return redirect('pedidos')


# ==========================================
# 2. VISTAS API REST (JSON)
# ==========================================

class ProductoViewSet(viewsets.ViewSet):

    def list(self, request):
        productos = ProductoDAO.obtener_todos()
        serializer = ProductoSerializer(productos, many=True)

        return Response(serializer.data)


class PedidoViewSet(viewsets.ViewSet):

    def list(self, request):
        pedidos = PedidoDAO.obtener_todos()
        serializer = PedidoSerializer(pedidos, many=True)

        return Response(serializer.data)