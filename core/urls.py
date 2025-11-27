from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_user, name='register_user'),
    path('register-staff/', views.register_staff, name='register_staff'),
    path('almacen/', views.listar_productos, name='listar_productos'),
    path('almacen/create/', views.crear_producto, name='crear_producto'),
    path('almacen/<int:pk>/', views.actualizar_producto, name='actualizar_producto'),
    path('almacen/<int:pk>/update-stock/', views.actualizar_stock, name='update_stock'),
    path('almacen/<int:pk>/update-precio/', views.actualizar_precio, name='update_precio'),
    path('ventas/', views.crear_venta, name='crear_venta'),
    path('ventas/list/', views.listar_ventas, name='listar_ventas'),
    path('users/', views.listar_usuarios, name='listar_usuarios'),
    path('users/<int:pk>/', views.actualizar_usuario, name='actualizar_usuario'),
]