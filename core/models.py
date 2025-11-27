from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class User(AbstractUser):
    # Tus campos adicionales (ej. rol)
    ROL_CHOICES = (
        ('admin', 'Administrador'),
        ('almacenero', 'Almacenero'),
        ('usuario', 'Usuario'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')

    # 👇 Opcional: si quieres evitar conflictos futuros (aunque ya no harán falta con AUTH_USER_MODEL)
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='core_user_set',  # ← custom related_name
    #     blank=True,
    #     help_text='The groups this user belongs to.',
    #     related_query_name='core_user',
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='core_user_set',
    #     blank=True,
    #     help_text='Specific permissions for this user.',
    #     related_query_name='core_user',
    # )

    def __str__(self):
        return self.username


class Almacen(models.Model):
    nombreproducto = models.CharField(max_length=255)
    tipoproducto = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    fechavencimiento = models.DateField(null=True, blank=True)  # ✅ Ahora es opcional
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