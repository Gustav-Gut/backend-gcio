from .models import Agency

import logging
logger = logging.getLogger('follow_up.services')

class AgencyService:
    @staticmethod
    def get_info(agency_id: int):
        """
        Obtiene información de una agencia por su ID.

        Args:
            agency_id (int): ID de la agencia

        Returns:
            Agency: Instancia de la agencia
        """
        return Agency.objects.get(id=agency_id)
        
