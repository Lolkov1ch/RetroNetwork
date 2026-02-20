from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('handle', 'display_name', 'email', 'is_staff')
    search_fields = ('username', 'handle', 'email', 'display_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('display_name', 'handle', 'bio', 'avatar', 'birth_date')}),
    )