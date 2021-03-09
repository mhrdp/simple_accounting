from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserExtended

# Register your models here.

# Register User AbstractModel from models.py
admin.site.register(UserExtended, UserAdmin)