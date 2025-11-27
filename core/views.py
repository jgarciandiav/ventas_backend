# core/views.py
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Almacen, ProductosVendidos

User = get_user_model()


# ========== PERMISOS PERSONALIZADOS ==========
class IsAdmin:
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'

class IsAlmaceneroOrAdmin:
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['almacenero', 'admin']

class IsUsuarioOrAlmaceneroOrAdmin:
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['usuario', 'almacenero', 'admin']


# ========== AUTH ==========
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login público"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Usuario y contraseña requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Usuario desactivado'}, status=status.HTTP_403_FORBIDDEN)

    # ✅ get_or_create: evita duplicados
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'username': user.username,
        'rol': user.rol,
        'user_id': user.id
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registro público (rol='usuario' por defecto)"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response(
            {'error': 'Faltan campos requeridos: username, email, password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Nombre de usuario ya existe'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email ya registrado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # ✅ Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol='usuario'  # ← por defecto, no se acepta desde frontend
        )
        user.is_active = True
        user.save()

        # ✅ get_or_create: evita "duplicate key"
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'rol': user.rol,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        # ✅ Limpiar usuario si falla
        if 'user' in locals():
            user.delete()
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# ========== ALMACEN ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_productos(request):
    """Listar productos (todos los roles)"""
    productos = Almacen.objects.all()
    data = [{
        'id': p.id,
        'nombre': p.nombre,
        'tipo': p.tipo,
        'precio_unitario': str(p.precio_unitario),
        'stock': p.stock,
        'fecha_vencimiento': p.fecha_vencimiento.isoformat() if p.fecha_vencimiento else None,
        'imagen': p.imagen or ''
    } for p in productos]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAlmaceneroOrAdmin])
def crear_producto(request):
    """Crear producto (almacenero o admin)"""
    print("✅ Datos recibidos:", request.data)
    print("✅ Tipos:", {k: type(v).__name__ for k, v in request.data.items()})
    try:
        data = request.data
        producto = Almacen.objects.create(
            nombre=data['nombre'],
            tipo=data['tipo'],
            precio_unitario=data['precio_unitario'],
            stock=data.get('stock', 0),
            fecha_vencimiento=data.get('fecha_vencimiento') or None,
            imagen=data.get('imagen', '')
        )
        return Response({
            'id': producto.id,
            'nombre': producto.nombre,
            'tipo': producto.tipo,
            'precio_unitario': str(producto.precio_unitario),
            'stock': producto.stock,
            'fecha_vencimiento': producto.fecha_vencimiento.isoformat() if producto.fecha_vencimiento else None,
            'imagen': producto.imagen
        }, status=status.HTTP_201_CREATED)
    except KeyError as e:
        return Response({'error': f'Campo requerido faltante: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAlmaceneroOrAdmin])
def actualizar_producto(request, pk):
    """Actualizar producto completo"""
    try:
        producto = Almacen.objects.get(pk=pk)
    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    try:
        producto.nombre = data.get('nombre', producto.nombre)
        producto.tipo = data.get('tipo', producto.tipo)
        producto.precio_unitario = data.get('precio_unitario', producto.precio_unitario)
        producto.stock = data.get('stock', producto.stock)
        producto.fecha_vencimiento = data.get('fecha_vencimiento') or producto.fecha_vencimiento
        producto.imagen = data.get('imagen', producto.imagen)
        producto.save()

        return Response({
            'id': producto.id,
            'nombre': producto.nombre,
            'tipo': producto.tipo,
            'precio_unitario': str(producto.precio_unitario),
            'stock': producto.stock,
            'fecha_vencimiento': producto.fecha_vencimiento.isoformat() if producto.fecha_vencimiento else None,
            'imagen': producto.imagen
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAlmaceneroOrAdmin])
def actualizar_stock(request, pk):
    """Actualizar solo stock"""
    try:
        producto = Almacen.objects.get(pk=pk)
    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    stock = request.data.get('stock')
    if stock is None:
        return Response({'error': 'Campo "stock" requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        stock = int(stock)
        if stock < 0:
            raise ValueError
    except:
        return Response({'error': 'Stock debe ser entero ≥ 0'}, status=status.HTTP_400_BAD_REQUEST)

    producto.stock = stock
    producto.save()
    return Response({
        'id': producto.id,
        'nombre': producto.nombre,
        'stock': producto.stock
    })


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def actualizar_precio(request, pk):
    """Actualizar solo precio (solo admin)"""
    try:
        producto = Almacen.objects.get(pk=pk)
    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    precio = request.data.get('precio_unitario')
    if precio is None:
        return Response({'error': 'Campo "precio_unitario" requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        precio = float(precio)
        if precio <= 0:
            raise ValueError
    except:
        return Response({'error': 'Precio debe ser número > 0'}, status=status.HTTP_400_BAD_REQUEST)

    producto.precio_unitario = precio
    producto.save()
    return Response({
        'id': producto.id,
        'nombre': producto.nombre,
        'precio_unitario': str(producto.precio_unitario)
    })


# ========== VENTAS ==========
@api_view(['POST'])
@permission_classes([IsUsuarioOrAlmaceneroOrAdmin])
def crear_venta(request):
    """Registrar venta"""
    try:
        data = request.data
        ventas = data.get('ventas', [])
        
        if not ventas:
            return Response({'error': 'No se enviaron productos'}, status=status.HTTP_400_BAD_REQUEST)

        total_venta = 0
        detalles = []

        for item in ventas:
            producto_id = item.get('producto_id')
            cantidad = item.get('cantidad', 1)

            try:
                producto = Almacen.objects.get(id=producto_id)
            except Almacen.DoesNotExist:
                return Response({'error': f'Producto no encontrado: {producto_id}'}, status=status.HTTP_404_NOT_FOUND)

            if producto.stock < cantidad:
                return Response({
                    'error': f'Stock insuficiente para {producto.nombre}',
                    'disponible': producto.stock,
                    'solicitado': cantidad
                }, status=status.HTTP_400_BAD_REQUEST)

            subtotal = float(producto.precio_unitario) * cantidad
            total_venta += subtotal

            # Crear registro
            venta = ProductosVendidos.objects.create(
                usuario=request.user,
                producto=producto,
                cantidad=cantidad,
                precio_total=subtotal,
                fecha=timezone.now()
            )
            detalles.append({
                'id': venta.id,
                'producto': producto.nombre,
                'cantidad': cantidad,
                'subtotal': subtotal
            })

            # Actualizar stock
            producto.stock -= cantidad
            producto.save()

        return Response({
            'mensaje': 'Venta registrada exitosamente',
            'total': total_venta,
            'detalles': detalles
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_ventas(request):
    """Listar ventas"""
    ventas = ProductosVendidos.objects.select_related('usuario', 'producto')
    
    # Filtro por fecha (opcional)
    fecha = request.GET.get('fecha')
    if fecha:
        ventas = ventas.filter(fecha__date=fecha)

    data = [{
        'id': v.id,
        'usuario': v.usuario.username,
        'producto_nombre': v.producto.nombre,
        'cantidad': v.cantidad,
        'precio_total': str(v.precio_total),
        'fecha': v.fecha.isoformat()
    } for v in ventas]
    return Response(data)


# ========== USUARIOS ==========
@api_view(['GET'])
@permission_classes([IsAdmin])
def listar_usuarios(request):
    """Listar usuarios (solo admin)"""
    usuarios = User.objects.all()
    data = [{
        'id': u.id,
        'username': u.username,
        'rol': u.rol,
        'is_active': u.is_active,
        'is_staff': u.is_staff
    } for u in usuarios]
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def actualizar_usuario(request, pk):
    """Actualizar usuario (solo admin)"""
    try:
        usuario = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    try:
        if 'rol' in data:
            if data['rol'] not in ['admin', 'almacenero', 'usuario']:
                return Response({'error': 'Rol inválido'}, status=status.HTTP_400_BAD_REQUEST)
            usuario.rol = data['rol']
        
        if 'is_active' in data:
            usuario.is_active = data['is_active']

        usuario.save()
        return Response({
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol,
            'is_active': usuario.is_active
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAdmin])  # ← solo admin puede
def register_staff(request):
    """Registrar staff (admin o almacenero) - solo para administradores"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    rol = request.data.get('rol')

    if not username or not email or not password or not rol:
        return Response(
            {'error': 'Faltan campos requeridos: username, email, password, rol'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if rol not in ['admin', 'almacenero']:
        return Response(
            {'error': 'Rol inválido. Solo se permiten: admin, almacenero'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Nombre de usuario ya existe'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email ya registrado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol=rol
        )
        user.is_active = True
        user.save()

        # ✅ Solo get_or_create (nada de create)
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'rol': user.rol,
            'is_active': user.is_active
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        if 'user' in locals():
            user.delete()
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )