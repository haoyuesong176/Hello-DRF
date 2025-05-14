from rest_framework import serializers
from django.contrib.auth.models import User 
from .models import FieldRecord, MyUser

class FieldRecordSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display')
    # booked_user_username = serializers.CharField(source='booked_user_id.username', allow_null=True)
    # booked_order_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z', allow_null=True)

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
            'booked_order_time'
        ]

class FieldRecordBookingSerializer(serializers.Serializer):
    id_list = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        error_messages={
            'not_a_list': 'id_list must be a list.',
            'empty': 'id_list cannot be empty.',
            'min_length': 'id_list must contain at least one item.'
        }
    )

    def validate_id_list(self, value):
        # 检查所有 ID 是否对应数据库中的记录
        existing_ids = set(FieldRecord.objects.filter(id__in=value).values_list('id', flat=True))
        invalid_ids = [vid for vid in value if vid not in existing_ids]

        if invalid_ids:
            raise serializers.ValidationError(f"The following ids do not exist: {invalid_ids}")

        # 检查这些记录是否都是 AVAILABLE 状态
        records = FieldRecord.objects.filter(id__in=value)
        unavailable_records = [r.id for r in records if r.status != FieldRecord.Status.AVAILABLE]
        if unavailable_records:
            raise serializers.ValidationError(f"The following records are not available: {unavailable_records}")

        return value

class FieldRecordUnbookSerializer(serializers.Serializer):
    id_list = serializers.ListField(child=serializers.IntegerField(), min_length=1)

    def validate_id_list(self, value):
        user = self.context['request'].user
        records = FieldRecord.objects.filter(id__in=value)

        if not records.exists():
            raise serializers.ValidationError("No matching records found.")

        non_existing_ids = set(value) - set(records.values_list('id', flat=True))
        if non_existing_ids:
            raise serializers.ValidationError(f"The following IDs do not exist: {list(non_existing_ids)}")

        for record in records:
            if record.booked_user_id != user:
                raise serializers.ValidationError(f"Field record {record.id} is not booked by you.")
            if record.status != FieldRecord.Status.BOOKED:
                raise serializers.ValidationError(f"Field record {record.id} is not in BOOKED status.")

        return value
    
class MyUserSerializer(serializers.ModelSerializer):
    # customized icon serializer 
    icon = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = [
            'username', 'phone', 'realname', 'nickname',
            'icon', 'level', 'balance', 'email', 'date_joined'
        ]
        read_only_fields = [
            'username', 'phone', 'realname', 'nickname',
            'level', 'balance', 'email', 'date_joined'
        ]
    
    def get_icon(self, obj):
        if obj.icon:
            request = self.context.get('request')
            photo_url = obj.icon.url
            return request.build_absolute_uri(photo_url) if request else photo_url
        return None