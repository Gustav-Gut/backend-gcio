from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class BookmarkPagination(PageNumberPagination):
    """Paginación estándar para bookmarks"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'data': data
        })

class PaginationMixin:
    """Mixin simple para añadir paginación a la vista BookmarkAPIView"""
    pagination_class = BookmarkPagination
    
    def paginate_results(self, data, request):
        """Método auxiliar para paginar resultados"""
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(data, request)
        
        if page is not None:
            return paginator.get_paginated_response(page)
        
        return Response(data)