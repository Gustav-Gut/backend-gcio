__all__ = ['AuthenticateService']

import os
import jwt
import datetime
from types import SimpleNamespace
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password

from .models import Agency, User
from apps.core.services import DatabasesUtils

class AuthenticateService:
   
    @staticmethod
    def authenticate_user_dynamic(user_rut, agency_id, password):
        """
        1. Obtiene la agencia de la base default
        2. Configura las conexiones dinámicas y guarda la agencia actual
        3. Busca al usuario en la base de datos dinámica
        4. Retorna el usuario si existe, None si no
        """
        try:
            # Obtener la agencia de la base default
            agency = Agency.objects.using('default').get(id=agency_id)
            
            # Configurar las conexiones dinámicas y guardar la agencia actual
            db_alias_gci = f"gci_{agency.name.lower()}"
            db_alias_gcli = f"gcli_{agency.name.lower()}"
            
            DatabasesUtils.get_dynamic_db_connection(db_alias_gci)
            DatabasesUtils.get_dynamic_db_connection(db_alias_gcli)
            DatabasesUtils.set_current_agency(agency)
            
            # Buscar al usuario en la base de datos dinámica
            user = User.objects.get(rut=user_rut)
            return user, None
            
        except Agency.DoesNotExist:
            return None, "Inmobiliaria no encontrada."
        except User.DoesNotExist:
            return None, "Usuario no encontrado en la base de datos dinámica."
    
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
