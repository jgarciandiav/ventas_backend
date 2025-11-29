# core/views.py
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Almacen, ProductosVendidos
from datetime import date

User = get_user_model()


# ========== PERMISOS ==========
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
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Usuario y contraseña requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Usuario desactivado'}, status=status.HTTP_403_FORBIDDEN)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'username': user.username,
        'rol': user.rol,
        'user_id': user.id
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'Faltan campos requeridos: username, email, password'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Nombre de usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email ya registrado'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol='usuario'
        )
        user.is_active = True
        user.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'rol': user.rol,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        if 'user' in locals():
            user.delete()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdmin])
def register_staff(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    rol = request.data.get('rol')

    if not username or not email or not password or not rol:
        return Response({'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    if rol not in ['admin', 'almacenero']:
        return Response({'error': 'Rol inválido. Solo se permiten: admin, almacenero'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Nombre de usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email ya registrado'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            rol=rol
        )
        user.is_active = True
        user.save()

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
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========== ALMACÉN ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_productos(request):
    productos = Almacen.objects.all()
    data = []
    for p in productos:
        item = {
            'id': p.id,
            'nombreproducto': p.nombreproducto,
            'tipoproducto': p.tipoproducto,
            'categoria': p.categoria,
            'fechavencimiento': p.fechavencimiento.isoformat() if p.fechavencimiento else None,
            'precio': float(p.precio) if p.precio else 0.0,
            'stock': p.stock
        }
        # ✅ Imagen segura
        if p.imagen:
            item['imagen'] = p.imagen.url
        else:
            item['imagen'] = None
        data.append(item)
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAlmaceneroOrAdmin])
def crear_producto(request):
    try:
        nombreproducto = request.POST.get('nombreproducto')
        tipoproducto = request.POST.get('tipoproducto')
        categoria = request.POST.get('categoria')
        fechavencimiento_str = request.POST.get('fechavencimiento')
        stock = request.POST.get('stock')
        imagen = request.FILES.get('imagen')

        if not all([nombreproducto, tipoproducto, categoria, fechavencimiento_str, stock]):
            return Response({'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Convertir string a objeto date
        try:
            fechavencimiento = date.fromisoformat(fechavencimiento_str)
        except (TypeError, ValueError):
            return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Crear producto
        producto = Almacen.objects.create(
            nombreproducto=nombreproducto,
            tipoproducto=tipoproducto,
            categoria=categoria,
            fechavencimiento=fechavencimiento,
            precio=0.00,  # ← el admin lo actualizará después
            stock=int(stock)
        )

        # ✅ Guardar imagen si existe
        if imagen:
            producto.imagen = imagen
            producto.save()

        # ✅ Respuesta segura
        return Response({
            'id': producto.id,
            'nombreproducto': producto.nombreproducto,
            'tipoproducto': producto.tipoproducto,
            'categoria': producto.categoria,
            'fechavencimiento': producto.fechavencimiento.isoformat(),
            'imagen': producto.imagen.url if producto.imagen else None,
            'precio': float(producto.precio),
            'stock': producto.stock
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("❌ Error en crear_producto:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAlmaceneroOrAdmin])
def actualizar_producto(request, pk):
    try:
        producto = Almacen.objects.get(pk=pk)
        
        # ✅ Solo actualizar campos permitidos
        nombreproducto = request.POST.get('nombreproducto')
        tipoproducto = request.POST.get('tipoproducto')
        categoria = request.POST.get('categoria')
        fechavencimiento_str = request.POST.get('fechavencimiento')
        stock = request.POST.get('stock')
        imagen = request.FILES.get('imagen')

        if nombreproducto:
            producto.nombreproducto = nombreproducto
        if tipoproducto:
            producto.tipoproducto = tipoproducto
        if categoria:
            producto.categoria = categoria
        if stock:
            producto.stock = int(stock)
        
        # ✅ Manejar fecha correctamente
        if fechavencimiento_str:
            try:
                producto.fechavencimiento = date.fromisoformat(fechavencimiento_str)
            except (TypeError, ValueError):
                return Response({'error': 'Formato de fecha inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ Guardar imagen si existe
        if imagen:
            producto.imagen = imagen

        producto.save()

        return Response({
            'id': producto.id,
            'nombreproducto': producto.nombreproducto,
            'tipoproducto': producto.tipoproducto,
            'categoria': producto.categoria,
            'fechavencimiento': producto.fechavencimiento.isoformat() if producto.fechavencimiento else None,
            'imagen': producto.imagen.url if producto.imagen else None,
            'precio': float(producto.precio),
            'stock': producto.stock
        })

    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("❌ Error en actualizar_producto:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAlmaceneroOrAdmin])
def actualizar_stock(request, pk):
    try:
        producto = Almacen.objects.get(pk=pk)
        stock = request.data.get('stock')
        if stock is None:
            return Response({'error': 'Campo "stock" requerido'}, status=status.HTTP_400_BAD_REQUEST)
        producto.stock = int(stock)
        producto.save()
        return Response({
            'id': producto.id,
            'nombreproducto': producto.nombreproducto,
            'stock': producto.stock
        })
    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("❌ Error en actualizar_stock:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def actualizar_precio(request, pk):
    try:
        producto = Almacen.objects.get(pk=pk)
        precio = request.data.get('precio')
        if precio is None:
            return Response({'error': 'Campo "precio" requerido'}, status=status.HTTP_400_BAD_REQUEST)
        producto.precio = float(precio)
        producto.save()
        return Response({
            'id': producto.id,
            'nombreproducto': producto.nombreproducto,
            'precio': float(producto.precio)
        })
    except Almacen.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("❌ Error en actualizar_precio:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========== VENTAS ==========
@api_view(['POST'])
@permission_classes([IsUsuarioOrAlmaceneroOrAdmin])
def crear_venta(request):
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
                    'error': f'Stock insuficiente para {producto.nombreproducto}',
                    'disponible': producto.stock,
                    'solicitado': cantidad
                }, status=status.HTTP_400_BAD_REQUEST)

            subtotal = float(producto.precio) * cantidad
            total_venta += subtotal

            # Crear registro
            venta = ProductosVendidos.objects.create(
                nombreproducto=producto.nombreproducto,
                tipoproducto=producto.tipoproducto,
                categoria=producto.categoria,
                precio_unitario=float(producto.precio),
                cantidad=cantidad
            )
            detalles.append({
                'id': venta.id,
                'producto': producto.nombreproducto,
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
        print("❌ Error en crear_venta:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdmin])
def listar_ventas_detalle(request):
    """Listar ventas con detalle de productos para reportes"""
    fecha = request.GET.get('fecha')
    
    # ✅ Consulta SIMPLE (tu modelo no tiene relaciones ForeignKey)
    ventas = ProductosVendidos.objects.order_by('-fechaventa')
    
    if fecha:
        ventas = ventas.filter(fechaventa__date=fecha)
    
    data = []
    for v in ventas:
        # ✅ Cálculo del precio total (no existe como campo en tu modelo)
        precio_total = float(v.precio_unitario) * v.cantidad
        
        data.append({
            'id': v.id,
            'producto': v.id,  # Usamos el ID como identificador
            'producto_nombre': v.nombreproducto,
            'categoria': v.categoria,
            'tipoproducto': v.tipoproducto,
            'cantidad': v.cantidad,
            'precio_unitario': float(v.precio_unitario),
            'precio_total': precio_total,  # Calculado dinámicamente
            'fecha': v.fechaventa.isoformat(),
            'usuario': 'Sistema'  # Valor por defecto (tu modelo no tiene usuario)
        })
    
    return Response(data)


# ========== USUARIOS ==========
@api_view(['GET'])
@permission_classes([IsAdmin])
def listar_usuarios(request):
    usuarios = User.objects.all()
    data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'rol': u.rol,
        'is_active': u.is_active
    } for u in usuarios]
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def actualizar_usuario(request, pk):
    try:
        usuario = User.objects.get(pk=pk)
        data = request.data
        
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
            'email': usuario.email,
            'rol': usuario.rol,
            'is_active': usuario.is_active
        })
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("❌ Error en actualizar_usuario:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)