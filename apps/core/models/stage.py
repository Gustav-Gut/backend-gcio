from django.db import models
from .project import Project

class Stage(models.Model):
    id_etapa = models.AutoField(primary_key=True)
    id_proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='id_proyecto')
    duracion_oferta = models.IntegerField()

    class Meta:
        db_table = 'etapa' 