# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),

    # Almacén
    path('almacen/', views.listar_productos, name='listar_productos'),  # GET → lista
    path('almacen/create/', views.crear_producto, name='crear_producto'),  # POST → crea
    path('almacen/<int:pk>/', views.actualizar_producto, name='actualizar_producto'),  # PUT
    path('almacen/<int:pk>/update-stock/', views.actualizar_stock, name='update_stock'),  # PATCH
    path('almacen/<int:pk>/update-precio/', views.actualizar_precio, name='update_precio'),  # PATCH

    # Ventas
    path('ventas/', views.crear_venta, name='crear_venta'),
    path('ventas/', views.listar_ventas, name='listar_ventas'),

    # Usuarios (solo admin)
    path('users/', views.listar_usuarios, name='listar_usuarios'),
    path('users/<int:pk>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('register/', views.register_user, name='register_user'),
    path('register-staff/', views.register_staff, name='register_staff'),
]