from django.contrib import admin

# Register your models here.
from .models import FieldRecord

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('name', 'introduction', 'teacher', 'price')
#     search_fields = list_display
#     list_filter = list_display

@admin.register(FieldRecord)
class FieldRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'field_name', 'price')
    search_fields = list_display
    list_filter = list_display

    
