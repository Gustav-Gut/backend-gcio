from django.db import models
from .task import Task
from .task_status import TaskStatus

class TaskHistory(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True, db_column='id_historial_tarea')
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='id_tarea', related_name='task_history')
    task_status_id = models.ForeignKey(TaskStatus, on_delete=models.CASCADE, db_column="id_estado_tarea")
    previous_assigned_username = models.CharField(max_length=30, blank=True, null=True, db_column='username_sso_antes_reasignacion')
    record_date = models.DateTimeField(db_column='fecha_registro')
    due_date = models.DateTimeField(db_column='fecha_limite')
    start_date = models.DateTimeField(blank=True, null=True, db_column='fecha_inicio')
    title = models.CharField(max_length=75, db_column='titulo')
    comment = models.CharField(max_length=1000, blank=True, null=True, db_column='comentario')
    attachments = models.CharField(max_length=255, blank=True, null=True, db_column='adjuntos')

    class Meta:
        db_table = 'historial_tarea'
        managed = False

    def __str__(self):
        return f"{self.title} - {self.record_date}"