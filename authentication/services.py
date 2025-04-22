# authentication/services.py
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
import os

from .models import Agency, User

class AuthenticateService:
    
    @staticmethod
    def authenticate_user_dynamic(client_rut, agency_id, password):
        """
        1. Con el agency_id, busca el nombre en la base default (modelo Inmobiliaria).
        2. Construye el alias de la base de datos dinámica: 'gci_{nombre_inmobiliaria}'.
        3. Usa esa conexión para consultar la tabla 'usuario' y verificar las credenciales.
        Retorna (usuario, None) si es exitoso, o (None, error_message) en caso contrario.
        """
        try:
            # Buscar la inmobiliaria en la base de datos default
            agency = Agency.objects.using('default').get(id=agency_id)
        except ObjectDoesNotExist:
            return None, "Inmobiliaria no encontrada."

        # Construir el alias de la base de datos dinámica
        agency_name = agency.name
        db_alias = f"gci_{agency_name.lower()}"

        # Obtener la conexión dinámica
        get_dynamic_db_connection(agency_name)

        try:
            # Buscar al usuario en la base de datos dinámica usando el alias
            user = User.objects.using(db_alias).get(rut=client_rut)
        except ObjectDoesNotExist:
            return None, "Usuario no encontrado en la base de datos dinámica."

        print("password --->", password)
        print("user password ---->", user.password)
        
        # Verificar el password (se supone que 'user.password' contiene el hash)
        stored_hash = user.password
        if stored_hash.startswith("$2y$"):
            print("user password ---->", stored_hash)
            stored_hash = "$2b$" + stored_hash[4:]
            
        if not check_password(password, stored_hash):
            return None, "Credenciales inválidas."

        return user, None

@staticmethod
def get_dynamic_db_connection(agency_name):
    """
    Dado el nombre de la inmobiliaria (por ejemplo, 'besalco'),
    construye el alias 'gci_besalco' y, si no existe en settings.DATABASES,
    lo agrega con la configuración necesaria.
    """
    alias = f"gci_{agency_name.lower()}"
    if alias not in settings.DATABASES:
        # Agregar la configuración dinámica
        settings.DATABASES[alias] = {
            'ENGINE': 'django.db.backends.mysql',  # Usando el backend de MySQL para MariaDB
            'NAME': alias,  # O la convención que uses para el nombre de la BD
            'USER': os.environ.get('MYSQL_USER', 'default_user'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'default_password'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'TIME_ZONE': settings.TIME_ZONE,
            'CONN_HEALTH_CHECKS': True,
            'CONN_MAX_AGE': getattr(settings, 'CONN_MAX_AGE', 0),
            'OPTIONS': {},
            'AUTOCOMMIT': True,
            'ATOMIC_REQUESTS': False,
            
        }
    # Retorna la conexión para el alias configurado
    return connections[alias]
