from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Almacen, ProductosVendidos

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'rol']
        extra_kwargs = {'rol': {'required': False}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            rol=validated_data.get('rol', 'usuario')
        )
        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if 'rol' in validated_data and (not request or request.user.rol != 'administrador'):
            raise serializers.ValidationError("Solo los administradores pueden cambiar el rol.")
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        if password:
            if password != password2:
                raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
            instance.set_password(password)
        return super().update(instance, validated_data)


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = '__all__'

    def validate_fechavencimiento(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("La fecha de vencimiento no puede ser en el pasado.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate(self, attrs):
        # Validación adicional: si se intenta cambiar 'precio', verificar rol
        request = self.context.get('request')
        if request and 'precio' in attrs:
            if request.user.rol != 'administrador':
                raise serializers.ValidationError({
                    'precio': 'Solo los administradores pueden modificar el precio.'
                })
        return attrs 

class AlmacenPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ['precio']


class AlmacenStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ['stock']


class ProductosVendidosSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductosVendidos
        fields = '__all__'
        read_only_fields = ['fechaventa', 'total']