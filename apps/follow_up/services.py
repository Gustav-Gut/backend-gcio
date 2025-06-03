from django.db.models import OuterRef, Subquery, Q, F
from django.utils import timezone
from datetime import datetime, time
from .models import Task, Evaluation, Client
from collections import Counter

import logging
logger = logging.getLogger('follow_up.services')

class FollowUpService:
    @staticmethod
    def _get_tasks(user_rut: int, date_filter: Q):
        """
        Función base para obtener tareas con filtros de fecha específicos.
        """
        max_date_subquery = Subquery(
            Task.objects.filter(
                id=OuterRef('id')
            ).order_by('-task_history__record_date').values('task_history__record_date')[:1]
        )
        
        return Task.objects.filter(
            system_id=1,
            task_status_id__label__in=['Nueva', 'En Ejecución'],
            actual_completion_date__isnull=True,
            task_type_id__label='Seguimiento',
            task_user__sso_username__username_sso=user_rut,
            task_user__sso_username__rut_gci=user_rut
        ).filter(date_filter).select_related(
            'task_status_id',
            'task_type_id',
        ).prefetch_related(
            'task_user__sso_username',
            'task_history'
        ).annotate(
            max_task_history_date=max_date_subquery,
        ).filter(
            Q(task_history__record_date=F('max_task_history_date')) |
            Q(max_task_history_date__isnull=True)
        ).all()

    @staticmethod
    def get_today_tasks(user_rut: int):
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))
        date_filter = Q(due_date__range=[start_of_day, end_of_day])
        return FollowUpService._get_tasks(user_rut, date_filter)

    @staticmethod
    def get_overdue_tasks(user_rut: int):
        today = timezone.now().date()
        date_filter = Q(due_date__lt=today)
        tasks = FollowUpService._get_tasks(user_rut, date_filter)
        return tasks
    
    @staticmethod
    def get_summary(user_rut: int, time_status: str):
        """
        Obtiene el resumen de tareas agrupadas por medio de entrada.
        
        Args:
            user_rut (int): RUT del usuario
            time_status (str): Estado temporal ('today' o 'overdue')
            
        Returns:
            dict: Resumen de tareas agrupadas por medio de entrada
        """
        tasks = FollowUpService.get_today_tasks(user_rut) if time_status == 'today' else FollowUpService.get_overdue_tasks(user_rut)

        task_ids = list(tasks.values_list('evaluation_id', flat=True))
        if task_ids:
            evaluations = Evaluation.objects.filter(
                id__in=task_ids
            ).select_related('visit_id')
            input_means_map = dict(
                evaluations.values_list('id', 'visit_id__input_means_id')
            )
        else:
            input_means_map = {}

        for task in tasks:
            task.input_means_id = input_means_map.get(task.evaluation_id.id)
            
        input_means_counter = Counter()
        means_map = {
            7:  'sales_room',
            4:  'centralizer',
            8:  'web_quoter',
            5:  'rrss',
            12: 'api',
        }

        for task in tasks:
            category = means_map.get(task.input_means_id, 'others')
            input_means_counter[category] += 1

        summary = {
            'sales_room': 0,
            'centralizer': 0,
            'web_quoter': 0,
            'rrss': 0,
            'api': 0,
            'others': 0
        }

        summary.update(input_means_counter)

        return {
            'status': 'success',
            'data': [{'means': key, 'quantity': value} for key, value in summary.items()]
        }
    
    @staticmethod
    def get_details(user_rut: int, time_status: str):
        """
        Obtiene los detalles de las tareas.
        """
        def format_rut(rut, dv):
            if rut:
                rut = str(rut).replace('.', '').replace('-', '')
                rut = '{:,}'.format(int(rut)).replace(',', '.')
                return f"{rut}-{dv}"
            return f""

        def format_date(date):
            if date is None:
                return None
            return date.strftime('%d-%m-%Y')
        
        means_map = {
            7:  'sales_room',
            4:  'centralizer',
            8:  'web_quoter',
            5:  'rrss',
            12: 'api',
        }
        
        tasks = FollowUpService.get_today_tasks(user_rut) if time_status == 'today' else FollowUpService.get_overdue_tasks(user_rut)
        tasks = tasks.select_related(
            'task_status_id',
            'task_type_id',
            'system_id',
            'task_user__sso_username'
        ).prefetch_related(
            'task_history'
        )

        client_ids = [task.client_gci_id.id for task in tasks if task.client_gci_id]
        evaluation_ids = [task.evaluation_id.id for task in tasks if task.evaluation_id]
    
        if client_ids:
            clients = Client.objects.filter(id__in=client_ids)
            client_map = {client.id: client for client in clients}
        else:
            client_map = {}

        if evaluation_ids:
            evaluations = Evaluation.objects.filter(id__in=evaluation_ids).select_related(
                'visit_id',
                'project_id'
            )
            evaluation_map = {evaluation.id: evaluation for evaluation in evaluations}
        else:
            evaluation_map = {}
        
        table_data = []
        for task in tasks:
            client_id = task.client_gci_id.id if task.client_gci_id else None
            evaluation_id = task.evaluation_id.id if task.evaluation_id else None
            
            client = client_map.get(client_id)
            evaluation = evaluation_map.get(evaluation_id)
            visit = evaluation.visit_id if evaluation else None

            rut = "Sin Rut"
            name = "Sin Nombre"

            if client:
                if client.type == 'NATURAL':
                    client_id = client.id
                    rut = format_rut(client.person_rut, client.person_rut_dv)
                    name = f"{client.person_name.strip()} {client.person_lastname.strip()}".strip().title()
                else:
                    client_id = client.id
                    rut = format_rut(client.company_rut, client.company_rut_dv)
                    name = client.company_name.strip().title()
            
            means = means_map.get(visit.input_means_id if visit else None, 'others')

            table_data.append({
                'id': task.id,
                'clientId': client_id,
                'rut': rut,
                'name': name,
                'project': evaluation.project_id.label.strip().title() if evaluation and evaluation.project_id else None,
                'contactDate': format_date(evaluation.recontact_date if evaluation else None),
                'lastComment': evaluation.comment.strip().lower() if evaluation else None,
                'means': means
            })

        return {
            'status': 'success',
            'data': table_data
        }