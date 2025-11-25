from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Almacen, ProductosVendidos
from .serializers import (
    UserSerializer,
    AlmacenSerializer,
    AlmacenPrecioSerializer,
    AlmacenStockSerializer,
    ProductosVendidosSerializer
)

# core/views.py

from .permissions import IsAdmin, IsAdminOrAlmacenero, CanUpdatePrecio, IsOwnerOrAdmin  
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdmin()]
        elif self.action in ['list', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        if request.user.rol == 'administrador':
            return super().list(request, *args, **kwargs)
        return Response([UserSerializer(request.user).data])


class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [IsAdminOrAlmacenero]  # Base: admin o almacenero
    filterset_fields = ['categoria', 'tipoproducto']

    def get_permissions(self):
        # Permisos específicos por acción
        if self.action in ['create', 'list', 'retrieve', 'destroy']:
            # Almacenero y admin pueden crear, listar, ver y borrar
            return [IsAdminOrAlmacenero()]
        elif self.action in ['update', 'partial_update']:
            # Para actualizar: permitir campos, pero validar precio con permiso extra
            return [IsAdminOrAlmacenero(), CanUpdatePrecio()]
        elif self.action == 'actualizar_precio':
            # El endpoint dedicado /precio/ solo para admin
            return [IsAdmin()]
        elif self.action == 'actualizar_stock':
            return [IsAdminOrAlmacenero()]
        elif self.action == 'reabastecer':
            return [IsAdminOrAlmacenero()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'actualizar_precio':
            return AlmacenPrecioSerializer
        if self.action == 'actualizar_stock':
            return AlmacenStockSerializer
        return AlmacenSerializer

    @action(detail=True, methods=['patch'], url_path='precio')
    def actualizar_precio(self, request, pk=None):
        """Endpoint dedicado: solo admin puede usarlo"""
        almacen = self.get_object()
        serializer = AlmacenPrecioSerializer(almacen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='stock')
    def actualizar_stock(self, request, pk=None):
        almacen = self.get_object()
        serializer = AlmacenStockSerializer(almacen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reabastecer')
    def reabastecer(self, request, pk=None):
        almacen = self.get_object()
        try:
            cantidad = int(request.data.get('cantidad', 0))
        except (TypeError, ValueError):
            return Response({"error": "Cantidad debe ser un número entero."}, status=status.HTTP_400_BAD_REQUEST)
        if cantidad <= 0:
            return Response({"error": "Cantidad debe ser mayor que 0."}, status=status.HTTP_400_BAD_REQUEST)
        almacen.stock += cantidad
        almacen.save()
        return Response({
            "mensaje": f"{cantidad} unidades añadidas.",
            "stock_actual": almacen.stock
        })

class ProductosVendidosViewSet(viewsets.ModelViewSet):
    queryset = ProductosVendidos.objects.all()
    serializer_class = ProductosVendidosSerializer
    permission_classes = [IsAdminOrAlmacenero]
    filterset_fields = ['fechaventa']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        if fecha:
            queryset = queryset.filter(fechaventa=fecha)
        elif fecha_inicio and fecha_fin:
            queryset = queryset.filter(fechaventa__range=[fecha_inicio, fecha_fin])
        elif fecha_inicio:
            queryset = queryset.filter(fechaventa__gte=fecha_inicio)
        elif fecha_fin:
            queryset = queryset.filter(fechaventa__lte=fecha_fin)
        return queryset

    def create(self, request, *args, **kwargs):
        almacen_id = request.data.get('almacen_id')
        cantidad = request.data.get('cantidad', 1)

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            return Response({"error": "Cantidad debe ser un número entero."}, status=status.HTTP_400_BAD_REQUEST)

        if not almacen_id:
            return Response({"error": "Se requiere 'almacen_id'."}, status=status.HTTP_400_BAD_REQUEST)
        if cantidad < 1:
            return Response({"error": "La cantidad debe ser al menos 1."}, status=status.HTTP_400_BAD_REQUEST)

        almacen = get_object_or_404(Almacen, id=almacen_id)

        from datetime import date
        if almacen.fechavencimiento < date.today():
            return Response({
                "error": f"El producto '{almacen.nombreproducto}' está vencido ({almacen.fechavencimiento})."
            }, status=status.HTTP_400_BAD_REQUEST)

        if almacen.stock < cantidad:
            return Response({
                "error": f"Stock insuficiente. Disponible: {almacen.stock}, solicitado: {cantidad}."
            }, status=status.HTTP_400_BAD_REQUEST)

        venta = ProductosVendidos.objects.create(
            nombreproducto=almacen.nombreproducto,
            tipoproducto=almacen.tipoproducto,
            categoria=almacen.categoria,
            precio_unitario=almacen.precio,
            cantidad=cantidad
        )

        almacen.stock -= cantidad
        almacen.save()

        serializer = self.get_serializer(venta)
        return Response({
            "venta": serializer.data,
            "mensaje": f"{cantidad} unidad(es) vendida(s) exitosamente.",
            "stock_restante": almacen.stock
        }, status=status.HTTP_201_CREATED)