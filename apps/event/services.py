from datetime import datetime
import calendar

from ..core.models.event import PersonalEvent

import logging
logger = logging.getLogger('follow_up.services')

class EventService:
    @staticmethod
    def personal_events(user_rut: int, year: int, month: int):
        """
        Obtiene eventos para un usuario en un mes específico.
        
        Args:
            rut (int): RUT del usuario
            year (int): Año (ejemplo: 2024)
            month (int): Mes (1-12)
            
        Returns:
            QuerySet: Eventos con el nombre del emisor
        """
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        
        return PersonalEvent.objects.filter(
            rut=user_rut,
            date__range=(first_day, last_day)
        ).exclude(
            title='CLIENTE'
        ).select_related('emisor').order_by('date')
