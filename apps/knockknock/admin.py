from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Web3Auth

class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'register_type')

    ordering = ['username']


# admin.site.register(User, UserAdmin)
admin.site.register(User)
admin.site.register(Web3Auth)