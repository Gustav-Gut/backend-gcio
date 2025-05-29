from django.db import models

class System(models.Model):
    database = 'gcli'

    id = models.AutoField(primary_key=True, db_column='id_sistema')
    label = models.CharField(max_length=15, db_column='glosa_sistema')

    class Meta:
        db_table = 'sistema'
        managed = False

    def __str__(self):
        return self.system_gloss