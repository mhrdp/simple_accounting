from django.contrib import admin

from .models import (
    ExpenseCategory, SubCategory, Journal, Product
)

# Register your models here.
admin.site.register(ExpenseCategory)
admin.site.register(SubCategory)
admin.site.register(Journal)
admin.site.register(Product)