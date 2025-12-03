🚀 MultiTiendas - Backend Installation Guide
Guía para instalar y configurar el backend de MultiTiendas en una nueva máquina.

📋 Requisitos previos
	✅ Python 3.8+
	✅ PostgreSQL 12+
	✅ Node.js (solo si usas frontend estático)
🛠️ Pasos de instalación

1. Crear entorno virtual
	bash

		python -m venv venv
                venv\Scripts\activate

2. Instalar dependencias

	pip install -r requirements.txt

3. Configurar base de datos PostgreSQL
	a) Crear base de datos y usuario:

		psql o pgAdminCREATE DATABASE ventas;

	b) Actualizar settings.py:
		ventas_backend/
		settings.py DATABASES = 'default':         
		'ENGINE': 'django.db.backends.postgresql',        
		'NAME': 'ventas',        
		'USER': 'administrador de postgresql',        
		'PASSWORD': 'tu_contraseña_segura',  # 👈 Cambia esto        
		'HOST': 'localhost',        
		'PORT': '5432',

4. Aplicar migraciones

	python manage.py makemigrations
	python manage.py migrate

5. Crear superusuario

	python manage.py createsuperuser  # Sigue las instrucciones (usuario: admin, email: opcional, password: admin123)

6. Configurar email para recuperación de contraseña
	En settings.py, añade:

	# Configuración de email (ejemplo con Gmail)EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend
	'EMAIL_HOST = 'smtp.gmail.com'
	EMAIL_PORT = 587EMAIL_USE_TLS = True
	EMAIL_HOST_USER = 'tu_email@gmail.com'        # 👈 Tu emailEMAIL_HOST_PASSWORD = 'tu_contraseña_de_app'  # 👈 Contraseña de App
	DEFAULT_FROM_EMAIL = 'MultiTiendas <no-reply@multitiendas.com>'

⚠️ Importante para Gmail: Usa una Contraseña de App, no tu contraseña normal.

8. Iniciar el servidor de desarrollo

python manage.py runserver

✅ Backend listo en: http://127.0.0.1:8000

🔌 Endpoints principales
Endpoint             Método  Descripción
/api/login/          POST    Iniciar sesión
/api/register/       POST    Registrar cliente
/api/password-reset/ POST    Solicitar recuperación
/api/almacen/        GET     Listar productos
/api/ventas/         POST    Registrar venta
📞 Soporte
Para problemas de instalación, contacta al equipo de desarrollo:

📧 email@multitiendas.com
📱 WhatsApp: +51 999 888 777
✅ Listo para conectar con el frontend en http://127.0.0.1:5500

¡Bienvenido a MultiTiendas! 🛒
