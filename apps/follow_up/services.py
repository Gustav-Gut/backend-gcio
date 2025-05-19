from django.db.models import OuterRef, Subquery, Q, F
from django.utils import timezone
from datetime import datetime, time
from .models import Task, TaskHistory

class FollowUpService:
    @staticmethod
    def get_today_tasks(user_rut: int):
        # Obtener fecha actual
        today = timezone.now().date()
        # Crear datetime para inicio y fin del día
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))

        subquery_max_fecha = Subquery(
            Task.objects.filter(
                task_id=OuterRef('task_id')
            ).order_by(
                '-task_history__record_date'
            ).values(
                'task_history__record_date'
            )[:1]
        )

        return Task.objects.using('gcli_legacy_tenant').filter(
            system_id=1,
            task_status_id__task_status_gloss__in=['Nueva', 'En Ejecución'],
            due_date__range=[start_of_day, end_of_day],
            actual_completion_date__isnull=True,
            task_type_id__task_type_label='Seguimiento',
            task_user__sso_username__username_sso=user_rut,
            task_user__sso_username__rut_gci=user_rut
        ).select_related(
            'task_status_id',
            'task_type_id'
        ).prefetch_related(
            'task_user__sso_username',
            'task_history'
        ).annotate(
            max_task_history_date=subquery_max_fecha
        ).filter(
            Q(task_history__record_date=F('max_task_history_date')) |
            Q(max_task_history_date__isnull=True)
        ).all()

    @staticmethod
    def get_overdue_tasks(user_rut: int):
        # Obtener fecha actual
        today = timezone.now().date()
        # Crear datetime para fin del día
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))

        subquery_max_fecha = Subquery(
            Task.objects.filter(
                task_id=OuterRef('task_id')
            ).order_by('-task_history__record_date').values('task_history__record_date')[:1]
        )

        return Task.objects.using('gcli_legacy_tenant').filter(
            system_id=1,
            task_status_id__task_status_gloss__in=['Nueva', 'En Ejecución'],
            due_date__lt=end_of_day,
            actual_completion_date__isnull=True,
            task_type_id__task_type_label='Seguimiento',
            task_user__sso_username__username_sso=user_rut,
            task_user__sso_username__rut_gci=user_rut
        ).select_related(
            'task_status_id',
            'task_type_id'
        ).prefetch_related(
            'task_user__sso_username',
            'task_history'
        ).annotate(
            max_task_history_date=subquery_max_fecha
        ).filter(
            Q(task_history__record_date=F('max_task_history_date')) |
            Q(max_task_history_date__isnull=True)
        ).all()