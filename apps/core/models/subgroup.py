from django.db import models
from .stage import Stage

class Subgroup(models.Model):
    id_subagrupacion = models.AutoField(primary_key=True)
    id_etapa = models.ForeignKey(Stage, on_delete=models.CASCADE, db_column='id_etapa')

    class Meta:
        db_table = 'subagrupacion' 