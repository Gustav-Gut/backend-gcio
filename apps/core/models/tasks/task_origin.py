from django.db import models

class TaskOrigin(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True, db_column='id_origen_tarea')
    label = models.CharField(max_length=50, db_column='glosa_origen_tarea')
    system_id = models.IntegerField(blank=True, null=True, db_column='id_sistema')

    class Meta:
        db_table = 'origen_tarea'
        managed = False

    def __str__(self):
        return self.task_origin_gloss