from django.db import models

class Visit(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_visita')
    input_means_id = models.IntegerField(blank=False, null=False, db_column='id_via_ingreso')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'visita'
        managed = False