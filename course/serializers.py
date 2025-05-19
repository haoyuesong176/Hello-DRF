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
            'status_label'
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

class FieldRecordMatchingSerializer(serializers.Serializer):
    id_list = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    payment_type = serializers.ChoiceField(choices=FieldRecord.PaymentType.choices)
    min_level = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        min_value=1.0,
        max_value=5.0
    )


class MatchingUserInfoSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['id', 'nickname', 'level', 'icon']

    def get_icon(self, obj):
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            return request.build_absolute_uri(obj.icon.url)
        return None


class ConfirmMatchSerializer(serializers.Serializer):
    id_list = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="List of FieldRecord IDs to mark as matched."
    )


class FieldRecordScheduleSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    opponent_icon_url = serializers.SerializerMethodField()
    time = serializers.TimeField(format='%H:%M', read_only=True)  # 格式化时间为 HH:MM

    class Meta:
        model = FieldRecord
        fields = [
            'time',
            'field_name',
            'status',
            'status_label',
            'opponent_icon_url'
        ]

    def get_status_label(self, obj):
        return obj.get_status_display()

    def get_opponent_icon_url(self, obj):
        request = self.context.get('request')
        if obj.status == FieldRecord.Status.MATCHED:
            user = self.context['request'].user
            opponent = None

            # 查找除了当前用户以外的其他参与者
            if obj.matched_user_id and obj.matched_user_id != user:
                opponent = obj.matched_user_id
            elif obj.matching_user_id and obj.matching_user_id != user:
                opponent = obj.matching_user_id
            elif obj.booked_user_id and obj.booked_user_id != user:
                opponent = obj.booked_user_id  # 备用情况

            if opponent and opponent.icon:
                return request.build_absolute_uri(opponent.icon.url)
        return None