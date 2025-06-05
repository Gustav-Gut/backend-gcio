from django.db import models
from .product import Product

class Reservation(models.Model):
    id = models.IntegerField(blank=False, null=False, primary_key=True, db_column='id_oferta')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='id')
    status = models.CharField(max_length=20, db_column='estado')
    created_at = models.DateTimeField(blank=False, null=False, db_column='fecha_creacion')

    def __str__(self):
        return self.id
    
    class Meta:
        db_table = 'oferta'
