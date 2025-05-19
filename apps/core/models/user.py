from django.db import models

class User(models.Model):
    database = 'gcli'

    username_sso = models.CharField(primary_key=True, max_length=30, db_column='username_sso')
    rut_gci = models.IntegerField(blank=True, null=True, db_column='rut_gci')
    password_gci = models.CharField(max_length=128, blank=True, null=True, db_column='password_gci')
    username_pvi = models.CharField(max_length=15, blank=True, null=True, db_column='username_pvi')
    password_pvi = models.CharField(max_length=255, blank=True, null=True, db_column='password_pvi')
    usuario_id_pvi = models.IntegerField(blank=True, null=True, db_column='usuario_id_pvi')
    email = models.CharField(max_length=45, blank=True, null=True, db_column='e_mail')
    first_name = models.CharField(max_length=45, blank=True, null=True, db_column='nombres')
    last_name = models.CharField(max_length=45, blank=True, null=True, db_column='apellido_paterno')
    mother_last_name = models.CharField(max_length=45, blank=True, null=True, db_column='apellido_materno')
    street = models.CharField(max_length=30, blank=True, null=True, db_column='dir_calle')
    number = models.CharField(max_length=11, blank=True, null=True, db_column='dir_numero')
    apartment = models.CharField(max_length=5, blank=True, null=True, db_column='dir_depto')
    phone = models.CharField(max_length=15, blank=True, null=True, db_column='telefono')
    position = models.CharField(max_length=255, db_column='cargo')
    active = models.IntegerField(blank=True, null=True, db_column='activo')
    edit_date = models.DateTimeField(blank=True, null=True, db_column='fecha_edicion')

    def __str__(self):
        return self.first_name

    class Meta:
        managed = False
        db_table = 'usuario'
