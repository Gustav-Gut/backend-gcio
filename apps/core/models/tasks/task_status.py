from django.db import models

class TaskStatus(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True, db_column='id_estado_tarea')
    label = models.CharField(max_length=50, db_column='glosa_estado_tarea')

    class Meta:
        db_table = 'estado_tarea'
        managed = False

    def __str__(self):
        return self.label