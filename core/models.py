from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('almacenero', 'Almacenero'),
        ('usuario', 'Usuario'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Almacen(models.Model):
    nombreproducto = models.CharField(max_length=255)
    tipoproducto = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    fechavencimiento = models.DateField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.nombreproducto} (stock: {self.stock})"

    class Meta:
        ordering = ['nombreproducto']


class ProductosVendidos(models.Model):
    nombreproducto = models.CharField(max_length=255)
    tipoproducto = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    fechaventa = models.DateField(auto_now_add=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.nombreproducto} ({self.total})"

    class Meta:
        ordering = ['-fechaventa']