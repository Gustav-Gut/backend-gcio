from ..services import DatabasesUtils

class AgencyDatabaseRouter:
    def db_for_read(self, model, **hints):
        agency = DatabasesUtils.get_current_agency()
        
        # Obtener qué BD usar del modelo
        db_type = getattr(model, 'database', 'default')  # Si no se especifica, usa default
        
        if db_type == 'default':
            return 'default'
            
        if agency and db_type in ['gci', 'gcli']:
            db_alias = f"{db_type}_{agency.name.lower()}"
            DatabasesUtils.get_dynamic_db_connection(db_alias)
            return db_alias
            
        return 'default'

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)