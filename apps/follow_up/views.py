from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import FollowUpService

class FollowUpViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request, *args, **kwargs):
        time_status = request.query_params.get('time_status', 'today')
        user_rut = request.headers.get('X-User-Rut')

        if time_status not in ['today', 'overdue']:
            return Response({
                'status': 'error',
                'message': 'time_status must be either "today" or "overdue"'
            }, status=400)

        try:
            result = FollowUpService.get_summary(user_rut, time_status)
            return Response(result)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)
        
    @action(detail=False, methods=['get'], url_path='details')
    def details(self, request, *args, **kwargs):
        time_status = request.query_params.get('time_status', 'today')
        user_rut = request.headers.get('X-User-Rut')

        if time_status not in ['today', 'overdue']:
            return Response({
                'status': 'error',
                'message': 'time_status must be either "today" or "overdue"'
            }, status=400)

        try:
            result = FollowUpService.get_details(user_rut, time_status)
            return Response(result)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)
        