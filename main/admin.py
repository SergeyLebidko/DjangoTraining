from django.contrib import admin
from .models import Client, Product, Order


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('title', 'credit_limit', 'vip')
    list_display_links = ('title',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'balance', 'price')
    list_display_links = ('title',)


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ('client', 'product', 'count', 'dt_create')
    list_display_links = ('client', 'product')
    raw_id_fields = ('client', 'product')
