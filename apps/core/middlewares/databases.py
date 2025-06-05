from ..services import DatabasesUtils

class DynamicDatabaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agency = DatabasesUtils.get_agency_from_request(request)
        if agency:
            # Siempre crear ambas conexiones
            db_alias_gci = f"gci_{agency.name.lower()}"
            db_alias_gcli = f"gcli_{agency.name.lower()}"
            
            DatabasesUtils.get_dynamic_db_connection(db_alias_gci)
            DatabasesUtils.get_dynamic_db_connection(db_alias_gcli)
            
            # Guardar la inmobiliaria actual para el router
            DatabasesUtils.set_current_agency(agency)
        
        response = self.get_response(request)
        
        # Limpiar conexiones no usadas
        DatabasesUtils.cleanup_unused_connections()
        
        return response