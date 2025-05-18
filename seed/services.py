from .models import PortalTypes

import logging
from pprint import pformat
logger = logging.getLogger(__name__)
class SeedServices:
    @staticmethod
    def get_portal_type(request):
        """
        Servicio de pruebas, servira como base para futuros desarrollos. 
        En esta ocasion traera los tipos de portales de la tabla tipo_portal de planok_gci mediante manejo de ORM DRF.
        """
        user_rut = request.headers.get('X-User-Rut')
        agency_id = request.headers.get('X-Agency-Id')

        logger.debug("user_rut via headers → %r", user_rut)
        logger.debug("agency_id via headers → %r", agency_id)
        return PortalTypes.objects.all()