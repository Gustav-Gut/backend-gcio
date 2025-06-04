from django.db import models
from .user import UserGci

class UserSellsProject(models.Model):
    database = 'gci'

    rut = models.ForeignKey(UserGci, on_delete=models.CASCADE, db_column='rut')
    project_id = models.ForeignKey('Project', on_delete=models.CASCADE, db_column='id_proyecto')

    def __str__(self):
        return f"{self.rut} - {self.project_id}"
    
    class Meta:
        db_table = 'usuario_ventas_proyecto'
        managed = False
