from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
#django ORM - Crear

def validar_precio_positivo(value):
    if value <= 0:
        raise ValidationError('El precio debe ser un número mayor a cero.')

class Producto(models.Model):
    CATEGORIAS = [
        ('FAMILIARES', 'Familiares'),
        ('PARTY GAMES', 'Party Games'),
        ('ESTRATEGIA', 'Estrategia'),
    ]
    nombre = models.CharField(max_length=100)
    #Aquí se crea la relación del nombre con el precio, la relación del ForeignKey.
    precio = models.DecimalField(max_digits=6, 
                                 decimal_places=2,
                                 validators=[validar_precio_positivo])
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    disponible = models.BooleanField(default=True)

    # Soporte para archivos multimedia (Media Files)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

class Pedido(models.Model):
    ESTADOS = [
        ('RECIBIDO', 'Recibido'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('LISTO', 'Listo para Entrega'),
        ('ENTREGADO', 'Entregado'),
    ]

    cliente_nombre = models.CharField(max_length=100)
# Aquí se agrega la relación
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='pedidos',
        null=True,
        blank=True
    )

    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='RECIBIDO')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente_nombre} ({self.estado})"