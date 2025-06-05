from django.db import models

class Project(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_proyecto')
    label = models.CharField(max_length=64, db_column='glosa_proyecto')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'proyecto'
        managed = False