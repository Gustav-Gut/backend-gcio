from django.db import models
from .user import UserGci

class PersonalEvent(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_evento')
    rut = models.IntegerField(blank=False, null=False, db_column='rut')
    date = models.DateField(blank=False, null=False, db_column='fecha')
    create_at = models.DateTimeField(blank=False, null=False, db_column='fecha_creacion')
    title = models.CharField(max_length=100, blank=False, null=False, db_column='titulo')
    detail = models.TextField(blank=True, null=True, db_column='detalle')
    emisor = models.ForeignKey(
        UserGci,
        on_delete=models.DO_NOTHING,
        db_column='rut_emisor',
        to_field='rut',
        related_name='events_sent'
    )

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'eventos_personales'
        managed = False

class GeneralEvent(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_evento_general')
    date = models.DateTimeField(blank=False, null=False, db_column='fecha')
    title = models.CharField(max_length=100, blank=False, null=False, db_column='titulo')
    detail = models.TextField(blank=True, null=True, db_column='detalle')
    project_id = models.ForeignKey('Project', on_delete=models.CASCADE, db_column='id_proyecto')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'eventos_generales'
        managed = False