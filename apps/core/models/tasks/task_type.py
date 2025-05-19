from django.db import models

class TaskType(models.Model):
    database = 'gcli'

    task_type_id = models.AutoField(primary_key=True, db_column='id_tipo_tarea')
    task_type_label = models.CharField(max_length=50, db_column='glosa_tipo_tarea')
    task_type_days = models.IntegerField(blank=True, null=True, db_column='dias_tipo_tarea')
    system_id = models.IntegerField(db_column='id_sistema')
    task_type_description = models.CharField(max_length=200, blank=True, null=True, db_column='descripcion_glosa_tipo_tarea')

    class Meta:
        db_table = 'tipo_tarea'
        managed = False

    def __str__(self):
        return self.task_type_label