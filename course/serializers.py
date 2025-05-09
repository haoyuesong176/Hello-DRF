from rest_framework import serializers
from django.contrib.auth.models import User 
from .models import FieldRecord

# class CourseSerializer(serializers.ModelSerializer):
    
#     teacher = serializers.ReadOnlyField(source='teacher.username')

#     class Meta:
#         model = Course
#         fields = '__all__'
#         depth = 2

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']  # 只选择需要的字段

# # 定义FieldRecord模型的序列化器
# class FieldRecordSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)  # 嵌套User序列化器
    
#     class Meta:
#         model = FieldRecord
#         fields = [
#             'id',
#             'date',
#             'time',
#             'field_name',
#             'price',
#             'status',
#             'user',  # 包含完整的user信息
#         ]
#         depth = 1

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

# class FieldRecordSerializer(serializers.ModelSerializer):
#     status = serializers.ChoiceField(
#         choices=FieldRecord.Status.choices,
#         default=FieldRecord.Status.AVAILABLE,
#     )
#     status_label = serializers.SerializerMethodField()

#     # user = UserSerializer(read_only=True)  # 嵌套User序列化器
    
#     class Meta:
#         model = FieldRecord
#         fields = '__all__'
#         depth = 0
#         # fields = [
#         #     'id',
#         #     'date',
#         #     'time',
#         #     'field_name',
#         #     'price',
#         #     'status',
#         #     'status_label',
#         # ]

#     def get_status_label(self, obj):
#         return obj.get_status_display()

    