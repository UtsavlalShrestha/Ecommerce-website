from django.contrib import admin
from .models import ProductList
# Register your models here.
# admin.site.register(ProductList)


@admin.register(ProductList)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)