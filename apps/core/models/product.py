from django.db import models
from .subgroup import Subgroup

class Product(models.Model):
    id = models.AutoField(blank=False, null=False, primary_key=True, db_column='id_producto')
    id_subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE, db_column='id')

    class Meta:
        db_table = 'producto' 