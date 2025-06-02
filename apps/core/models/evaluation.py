from django.db import models
from .project import Project
from .visit import Visit
from .client import Client

class Evaluation(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_evaluacion')
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='id_proyecto')
    visit_id = models.ForeignKey(Visit, on_delete=models.CASCADE, db_column='id_visita')
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='id_cliente')
    recontact_date = models.DateField(blank=False, null=False, db_column='fecha_recontacto')
    comment = models.TextField(blank=False, null=False, db_column='comentario')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'evaluacion'
        managed = False