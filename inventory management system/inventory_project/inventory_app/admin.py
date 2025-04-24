from django.contrib import admin
from .models import Product, Sale, Supplier, Customer

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'price', 'added_on')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'total_price', 'date']  # updated
    list_filter = ['date']  # updated
    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = 'Total Price'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'email')
    search_fields = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name',)


# Register your models here.
