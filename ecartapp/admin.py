from django.contrib import admin
from ecartapp.models import product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
        list_display=['id','name','price','pdetails','cart','is_active']
        list_filter=['cart','price','is_active']
admin.site.register(product,ProductAdmin)