# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_user, name='register_user'),
    path('register-staff/', views.register_staff, name='register_staff'),
    
    # Almacén
    path('almacen/', views.listar_productos, name='listar_productos'),
    path('almacen/create/', views.crear_producto, name='crear_producto'),
    path('almacen/<int:pk>/', views.actualizar_producto, name='actualizar_producto'),
    path('almacen/<int:pk>/update-stock/', views.actualizar_stock, name='update_stock'),
    path('almacen/<int:pk>/update-precio/', views.actualizar_precio, name='update_precio'),
    
    # Ventas
    path('ventas/', views.crear_venta, name='crear_venta'),  # POST para crear
    path('ventas/list/', views.listar_ventas_detalle, name='listar_ventas_detalle'),  # GET para listar
    
    # Usuarios
    path('users/', views.listar_usuarios, name='listar_usuarios'),
    path('users/<int:pk>/', views.actualizar_usuario, name='actualizar_usuario'),

    # recuperacion de password
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),    
]