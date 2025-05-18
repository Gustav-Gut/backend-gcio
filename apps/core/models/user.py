from django.db import models

class User(models.Model):
    rut = models.IntegerField(blank=False, null=False, primary_key=True, db_column='rut')
    name = models.CharField(max_length=100, blank=False, null=False, db_column='nombre')
    lastname = models.CharField(max_length=100, blank=False, null=False, db_column='apellido1')
    password = models.CharField(max_length=100, blank=False, null=False, db_column='password')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'usuario'
        managed = False
