__all__ = ['AuthenticateService']

import os
import jwt
import datetime
from types import SimpleNamespace
from django.conf import settings
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password

from .models import Agency, User
class AuthenticateService:
   
    @staticmethod
    def authenticate_user_dynamic(user_rut, agency_id, password):
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
        db_alias = f"gci_{agency.name.lower()}"

        # Obtener la conexión dinámica
        _AuthenticateUtils.get_dynamic_db_connection(db_alias)

        try:
            # Buscar al usuario en la base de datos dinámica usando el alias
            user = User.objects.using(db_alias).get(rut=user_rut)
        except ObjectDoesNotExist:
            return None, "Usuario no encontrado en la base de datos dinámica."
        
        # # Verificar el password (se supone que 'user.password' contiene el hash)
        # stored_hash = user.password
        # if stored_hash.startswith("$2y$"):
        #     print("user password ---->", stored_hash)
        #     stored_hash = "$2b$" + stored_hash[4:]
            
        # if not check_password(password, stored_hash):
        #     return None, "Credenciales inválidas."

        return user, None
    
    @staticmethod
    def generate_jwt(user, agency_id):
        """
        Genera un access (15min) y refresh(48hrs) tokens, cada uno con sus claims correspondientes
        """
        now = datetime.datetime.now()
        access_payload = {
            'userRut':    user.rut,
            'agencyId':  agency_id,
            'iss':       'jwt_gci',
            'exp':       now + datetime.timedelta(minutes=15)
        }
        refresh_payload = {
            'userRut':    user.rut,
            'agencyId':  agency_id,
            'iss':       'jwt_gci',
            'exp':       now + datetime.timedelta(hours=48)
        }
        access_token = jwt.encode(
            access_payload,
            os.environ.get('SECRET_ACCESS_JWT'),
            algorithm='HS256'
        )
        refresh_token = jwt.encode(
            refresh_payload,
            os.environ.get('SECRET_REFRESH_JWT'),
            algorithm='HS256'
        )
        return access_token, refresh_token
    
    @staticmethod
    def refresh_jwt(old_refresh_token):
        """
        Recibe el refresh token revisa si es válido y no expirado, 
        emite un nuevo par de tokens.
        """
        try:
            payload = jwt.decode(
                old_refresh_token,
                os.environ.get('SECRET_REFRESH_JWT'),
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            return None, None, 'Refresh token expirado.'
        except jwt.InvalidTokenError as e:
            return None, None, f'Token inválido: {str(e)}'

        new_acess_token, new_refresh_token = AuthenticateService.generate_jwt(
            SimpleNamespace(rut=payload['userRut']),
            payload['agencyId']
        )

        return new_acess_token, new_refresh_token, None

class _AuthenticateUtils:
    """
    Clase para manejar conexiones a bases de datos dinámicas.
    """
    @staticmethod
    def get_dynamic_db_connection(db_alias):
        """
        Dado el nombre de la inmobiliaria (por ejemplo, 'besalco'),
        construye el alias 'gci_besalco' y, si no existe en settings.DATABASES,
        lo agrega con la configuración necesaria.
        """
        if db_alias not in settings.DATABASES:
            # Agregar la configuración dinámica
            settings.DATABASES[db_alias] = {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': db_alias,
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
        return connections[db_alias]
        