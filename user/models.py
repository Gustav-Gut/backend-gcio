from django.db import models

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True, db_column='usuario_id')
    username = models.CharField(max_length=150, db_column='username')
   
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'usuario'
        managed = False