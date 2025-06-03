from django.db import models

class Agency(models.Model):
    database = 'default'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id')
    name = models.CharField(max_length=300, blank=False, null=False, db_column='name')
    url = models.CharField(max_length=300, blank=False, null=False, db_column='url_inmobiliaria')
    bd = models.CharField(max_length=100, blank=False, null=False, db_column='bd_inmobiliaria')
    bd_tasks = models.CharField(max_length=100, blank=False, null=False, db_column='bd_clientes')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'inmobiliarias'
        managed = False
        