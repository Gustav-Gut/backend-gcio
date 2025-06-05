import os
import time
from django.conf import settings
from django.db import connections
from threading import local

_thread_locals = local()

class DatabasesUtils:
    
    def get_agency_from_request(request):
        """
        Extrae la inmobiliaria de los headers de Kong.
        Retorna None si no hay headers o son inválidos.
        """
        try:
            # Obtener el agency_id del header de Kong
            agency_id = request.headers.get('X-Agency-Id')
            if not agency_id:
                return None
                
            # Obtener la inmobiliaria
            # Importar aquí para evitar importación circular
            from apps.core.models import Agency
            return Agency.objects.get(id=agency_id)
            
        except (Agency.DoesNotExist, ValueError):
            return None
    
    def get_current_agency():
        """
        Obtiene la inmobiliaria actual del thread local.
        Retorna None si no hay inmobiliaria establecida.
        """
        return getattr(_thread_locals, 'agency', None)

    def set_current_agency(agency):
        """
        Establece la inmobiliaria actual en el thread local.
        """
        _thread_locals.agency = agency

    @staticmethod
    def get_dynamic_db_connection(db_alias):
        """
        Dado el nombre de la inmobiliaria (por ejemplo, 'besalco'),
        construye el alias 'gci_besalco' y, si no existe en settings.DATABASES,
        lo agrega con la configuración necesaria.
        """

        if db_alias.startswith('gcli_'):
            host = os.environ.get('DB_HOST_GCLI', 'localhost')
        else:
            host = os.environ.get('DB_HOST_GCI', 'localhost')
    
        if db_alias not in settings.DATABASES:
            # Agregar la configuración dinámica
            settings.DATABASES[db_alias] = {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': db_alias,
                'USER': os.environ.get('MYSQL_USER', 'default_user'),
                'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'default_password'),
                'HOST': host,
                'PORT': os.environ.get('DB_PORT', '3306'),
                'TIME_ZONE': settings.TIME_ZONE,
                'CONN_HEALTH_CHECKS': True,
                'CONN_MAX_AGE': getattr(settings, 'CONN_MAX_AGE', 0),
                'OPTIONS': {},
                'AUTOCOMMIT': True,
                'ATOMIC_REQUESTS': False,
                
            }
        return connections[db_alias]
    
    @staticmethod
    def cleanup_unused_connections():
        current_time = time.time()
        connection_timeout = int(os.environ.get('CONNECTION_TIMEOUT', 3600))
        for alias in list(settings.DATABASES.keys()):
            if alias.startswith(('gci_', 'gcli_')):
                last_used = getattr(connections[alias], 'last_used', 0)
                if current_time - last_used > connection_timeout:
                    connections[alias].close()
                    del settings.DATABASES[alias]