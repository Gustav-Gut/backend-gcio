from django.db import connection
from .models import PortalTypes

class SeedServices:
    @staticmethod
    def get_portal_type():
        """
        Servicio de pruebas, servira como base para futuros desarrollos. 
        En esta ocasion traera los tipos de portales de la tabla tipo_portal de planok_gci mediante manejo de ORM DRF.
        """
        return PortalTypes.objects.all()