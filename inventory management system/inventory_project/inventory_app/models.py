from django.db import models
from django.utils import timezone
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True) 
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        setting = Setting.objects.first()
        tax_rate = Decimal(setting.tax_rate) if setting else Decimal('0')
        return self.product.price * self.quantity * (Decimal('1') + tax_rate / Decimal('100'))
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"


class Setting(models.Model):
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Settings (Tax Rate: {self.tax_rate}%)"
