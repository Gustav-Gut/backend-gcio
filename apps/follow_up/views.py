# apps/follow_up/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import FollowUpService

class FollowUpViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request, *args, **kwargs):
        time_status = request.query_params.get('time_status', 'today')
        user_rut = request.headers.get('user_rut')

        if time_status == 'today':
            tasks = FollowUpService.get_today_tasks(user_rut)
        elif time_status == 'overdue':
            tasks = FollowUpService.get_overdue_tasks(user_rut)
        else:
            return Response({
                'status': 'error',
                'message': 'time_status must be either "today" or "overdue"'
            }, status=400)

        # Agrupar por medio de entrada
        summary = {
            'sales_room': 0,
            'centralizer': 0,
            'web_quoter': 0,
            'social_networks': 0,
            'api': 0,
            'others': 0
        }

        for task in tasks:
            entry_medium = task.entry_medium_pvi_id
            if entry_medium == 1:
                summary['sales_room'] += 1
            elif entry_medium == 2:
                summary['centralizer'] += 1
            elif entry_medium == 3:
                summary['web_quoter'] += 1
            elif entry_medium == 4:
                summary['social_networks'] += 1
            elif entry_medium == 5:
                summary['api'] += 1
            else:
                summary['others'] += 1

        return Response({
            'status': 'success',
            'data': [{'entry_medium': key, 'value': value} for key, value in summary.items()]
        })