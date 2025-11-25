# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Almacen, ProductosVendidos


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Añadimos 'rol' a las vistas
    list_display = ('username', 'rol', 'is_staff', 'is_superuser')
    list_filter = ('rol', 'is_staff', 'is_superuser')
    
    # Añadir 'rol' en los formularios
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rol',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('rol',)}),
    )


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ['nombreproducto', 'categoria', 'stock', 'fechavencimiento', 'precio']
    list_filter = ['categoria', 'tipoproducto']
    search_fields = ['nombreproducto']


@admin.register(ProductosVendidos)
class ProductosVendidosAdmin(admin.ModelAdmin):
    list_display = ['nombreproducto', 'cantidad', 'precio_unitario', 'total', 'fechaventa']
    list_filter = ['fechaventa', 'categoria']