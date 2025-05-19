from django.db import models
from .task_type import TaskType
from .system import System
from .task_origin import TaskOrigin
from .task_status import TaskStatus

class Task(models.Model):
    database = 'gcli'

    task_id = models.AutoField(primary_key=True, db_column='id_tarea')
    task_type_id = models.ForeignKey(TaskType, on_delete=models.CASCADE, db_column="id_tipo_tarea")
    system_id = models.ForeignKey(System, on_delete=models.CASCADE, db_column="id_sistema")
    task_origin_id = models.ForeignKey(TaskOrigin, on_delete=models.CASCADE, db_column="id_origen_tarea")
    task_status_id = models.ForeignKey(TaskStatus, on_delete=models.CASCADE, db_column="id_estado_tarea")
    title = models.CharField(max_length=100, db_column='titulo')
    details = models.CharField(max_length=2000, blank=True, null=True, db_column='detalle')
    creation_date = models.DateTimeField(db_column='fecha_creacion')
    start_date = models.DateTimeField(db_column='fecha_inicio')
    due_date = models.DateTimeField(db_column='fecha_limite')
    actual_completion_date = models.DateTimeField(db_column='fecha_real_termino')
    edit_date = models.DateTimeField(blank=True, null=True, db_column='fecha_edicion')
    successfully_completed = models.IntegerField(blank=True, null=True, db_column='finalizada_con_exito')
    owner_pvi_id = models.IntegerField(blank=True, null=True, db_column='id_propietario_pvi')
    property_pvi_id = models.IntegerField(blank=True, null=True, db_column='id_propiedad_pvi')
    tenant_pvi_id = models.IntegerField(blank=True, null=True, db_column='id_arrendatario_pvi')
    non_owner_pvi_id = models.IntegerField(blank=True, null=True, db_column='id_no_propietario_pvi')
    escalation_pvi = models.IntegerField(blank=True, null=True, db_column='escalamiento_pvi')
    entry_medium_pvi_id = models.IntegerField(blank=True, null=True, db_column='id_medio_ingreso_pvi')
    area_id = models.IntegerField(db_column='id_area')
    client_gci_id = models.IntegerField(blank=True, null=True, db_column='id_cliente_gci')
    product_gci_id = models.IntegerField(blank=True, null=True, db_column='id_producto_gci')
    offer_gci_id = models.IntegerField(blank=True, null=True, db_column='id_oferta_gci')
    promise_gci_id = models.IntegerField(blank=True, null=True, db_column='id_promesa_gci')
    evaluation_id = models.IntegerField(blank=True, null=True, db_column='id_evaluacion')
    evaluation_aborted = models.IntegerField(blank=True, null=True, db_column='evaluacion_abortada')
    reassigned = models.IntegerField(blank=True, null=True, db_column='reasignada')
    contact_centralizer_gci_id = models.IntegerField(blank=True, null=True, db_column='id_centralizador_contacto_gci')

    class Meta:
        db_table = 'tarea'
        managed = False

    def __str__(self):
        return self.title