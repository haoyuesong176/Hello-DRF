from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import FieldRecord, MyUser

@admin.register(FieldRecord)
class FieldRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'field_name', 'price')
    search_fields = list_display
    list_filter = list_display

@admin.register(MyUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'is_staff', 'is_superuser')

    
