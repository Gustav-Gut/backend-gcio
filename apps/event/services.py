from datetime import datetime, timedelta
import calendar

from .models import PersonalEvent, GeneralEvent, UserSellsProject, Project, Offer, Promise
from django.db.models import ExpressionWrapper, F, DateTimeField

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

    @staticmethod
    def general_events(user_rut: int, year: int, month: int):
        """
        Obtiene eventos generales para un usuario en un mes específico.
        
        Args:
            user_rut (int): RUT del usuario
            year (int): Año (ejemplo: 2024)
            month (int): Mes (1-12)
            
        Returns:
            QuerySet: Eventos generales ordenados por fecha
        """
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        return GeneralEvent.objects.filter(
            project_id__in=UserSellsProject.objects.filter(
                rut=user_rut
            ).values_list('project_id', flat=True),
            date__range=(first_day, last_day)
        ).order_by('date')

    @staticmethod
    def get_expiring_offers(rut: str, year: int, month: int):
        """
        Obtiene las ofertas por vencer para un usuario en un mes específico.
        
        Args:
            rut (str): RUT del usuario
            year (int): Año (ejemplo: 2024)
            month (int): Mes (1-12)
            
        Returns:
            list: Lista de ofertas por vencer
        """
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        
        # Get user's projects
        user_projects = Project.objects.filter(
            usuario_ventas_proyecto__rut=rut
        ).values_list('id_proyecto', flat=True)
        
        # Calculate expiration date using F() expressions
        expiration_date = ExpressionWrapper(
            F('fecha_creacion') + timedelta(days=F('producto__subagrupacion__etapa__duracion_oferta')),
            output_field=DateTimeField()
        )
        
        # Query using ORM
        offers = Offer.objects.filter(
            estado='EMITIDA'
        ).exclude(
            estado='CANCELADA'
        ).exclude(
            id_oferta__in=Promise.objects.filter(
                estado__in=['EMITIDA', 'CREADA']
            ).values_list('id_oferta', flat=True)
        ).filter(
            producto__subagrupacion__etapa__id_proyecto__in=user_projects
        ).annotate(
            fecha_termino=expiration_date
        ).filter(
            fecha_termino__range=[first_day, last_day]
        ).select_related(
            'producto__subagrupacion__etapa__id_proyecto'
        ).order_by('fecha_termino')
        
        results = []
        for offer in offers:
            results.append({
                'duracion_oferta': offer.producto.subagrupacion.etapa.duracion_oferta,
                'id_oferta': offer.id_oferta,
                'id_producto': offer.id_producto,
                'glosa_proyecto': offer.producto.subagrupacion.etapa.id_proyecto.glosa_proyecto,
                'fecha_termino': offer.fecha_termino,
                'aprobada': offer.aprobada
            })
            
        return results
