from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ProductList(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    description = models.CharField(max_length=100)
    quantity = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class CartItem(models.Model):
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'