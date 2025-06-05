from django.db import models
from .reservation import Reservation

class Promise(models.Model):
    id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE, db_column='id')
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'promesa' 
