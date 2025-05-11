from rest_framework import serializers
from django.contrib.auth.models import User 
from .models import FieldRecord

class FieldRecordSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display')
    booked_user_username = serializers.CharField(source='booked_user_id.username', allow_null=True)
    booked_order_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z', allow_null=True)

    class Meta:
        model = FieldRecord
        fields = [
            'id',
            'date',
            'time',
            'field_name',
            'price',
            'status',
            'status_label',
            'booked_user_id',
            'booked_user_username',
            'booked_order_time',
        ]
    