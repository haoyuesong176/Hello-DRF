from rest_framework import serializers

from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    
    teacher = serializers.ReadOnlyField(source='teacher.username')

    class Meta:
        model = Course
        fields = '__all__'
        depth = 2

# class CourseSerializer(serializers.HyperlinkedModelSerializer):
    
#     teacher = serializers.ReadOnlyField(source='teacher.username')

#     class Meta:
#         model = Course
#         fields = ('id', 'url', 'name', 'introduction', 'teacher', 'price', 'created_at', 'updated_at')

    