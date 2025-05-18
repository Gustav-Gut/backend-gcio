from django.db import models

class PortalTypes(models.Model):
    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_tipo_portal')
    description_portal_type = models.CharField(max_length=100, blank=True, null=True, db_column='glosa_tipo_portal')

    def __str__(self):
        return self.description_portal_type
    
    class Meta:
        db_table = 'tipo_portal'
        managed = False