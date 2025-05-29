from django.db import models
from .task_type import TaskType
from .system import System
from .task_origin import TaskOrigin
from .task_status import TaskStatus
from ..evaluation import Evaluation
from ..client import Client

class Task(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True, db_column='id_tarea')
    system_id = models.ForeignKey(System, on_delete=models.CASCADE, db_column="id_sistema")
    task_type_id = models.ForeignKey(TaskType, on_delete=models.CASCADE, db_column="id_tipo_tarea")
    task_origin_id = models.ForeignKey(TaskOrigin, on_delete=models.CASCADE, db_column="id_origen_tarea")
    task_status_id = models.ForeignKey(TaskStatus, on_delete=models.CASCADE, db_column="id_estado_tarea")
    client_gci_id = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='id_cliente_gci')
    due_date = models.DateTimeField(db_column='fecha_limite')
    actual_completion_date = models.DateTimeField(db_column='fecha_real_termino')
    title = models.CharField(max_length=100, db_column='titulo')
    details = models.CharField(max_length=2000, blank=True, null=True, db_column='detalle')
    evaluation_id = models.ForeignKey(Evaluation, on_delete=models.CASCADE, db_column='id_evaluacion')

    class Meta:
        db_table = 'tarea'
        managed = False

    def __str__(self):
        return self.id