from django.db import models

class Client(models.Model):
    database = 'gci'

    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_cliente')
    type = models.CharField(max_length=8, db_column='tipo')
    person_name = models.CharField(max_length=64, db_column='nat_nombre')
    person_lastname = models.CharField(max_length=64, db_column='nat_apellido1')
    person_rut = models.CharField(max_length=12, db_column='nat_rut')
    person_rut_dv = models.CharField(max_length=1, blank=True, null=True, db_column='nat_dv_rut')
    company_rut = models.CharField(max_length=12, db_column='emp_rut')
    company_rut_dv = models.CharField(max_length=1, db_column='emp_dv_rut')
    company_name = models.CharField(max_length=64, db_column='emp_razon_social')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'cliente'
        managed = False