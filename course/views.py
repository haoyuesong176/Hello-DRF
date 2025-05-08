from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets # not implemented 
from .models import Course, FieldRecord
from .serializers import CourseSerializer 
from collections import defaultdict
from datetime import date, timedelta

class FieldDictView(APIView):
    def get(self, request):
        start_date = date.today()
        end_date = start_date + timedelta(days=7)

        # 数据库层过滤：只捞出7天数据
        queryset = FieldRecord.objects.filter(date__gte=start_date, date__lt=end_date)

        FieldDict = defaultdict(lambda: defaultdict(dict))

        for record in queryset:
            date_str = record.date.isoformat()
            time_str = record.time.strftime('%H:%M')
            FieldDict[date_str][time_str][record.field_name] = record.value

        import json
        FieldDict = json.loads(json.dumps(FieldDict))

        return Response(FieldDict)


class CourseList(APIView):

    def get(self, request):
        queryset = Course.objects.all()
        s = CourseSerializer(instance=queryset, many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)

    def post(self, request):
        s = CourseSerializer(data=request.data)
        if s.is_valid():
            s.save(teacher=request.user)
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetail(APIView):

    @staticmethod
    def get_course(pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None 

    def get(self, request, pk):
        obj = self.get_course(pk)
        if obj:
            s = CourseSerializer(instance=obj)
            return Response(data=s.data, status=status.HTTP_200_OK)
        return Response(data={"msg": "Course not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        obj = self.get_course(pk)
        if obj:
            s = CourseSerializer(instance=obj, data=request.data, partial=True)
            if s.is_valid():
                s.save()
                return Response(data=s.data, status=status.HTTP_200_OK)
            else:
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"msg": "Course not exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        obj = self.get_course(pk)
        if obj:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data={"msg": "Course not exist"}, status=status.HTTP_404_NOT_FOUND)


# class GCourseList(generics.ListCreateAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer

#     def perform_create(self, serializer):
#         serializer.save(teacher=self.request.user)

# class GCourseDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer


# @api_view(["GET", "POST"])
# def course_list(request):
#     if request.method == "GET":
#         s = CourseSerializer(instance=Course.objects.all(), many=True)
#         return Response(data=s.data, status=status.HTTP_200_OK)

#     elif request.method == "POST":
#         s = CourseSerializer(data=request.data) # partial=True
#         if s.is_valid():
#             s.save(teacher=request.user)
#             return Response(data=s.data, status=status.HTTP_201_CREATED)
#         return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["GET", "PUT", "DELETE"])
# def course_detail(request, pk):

#     try:
#         course = Course.objects.get(pk=pk)
#     except Course.DoesNotExist:
#         return Response(data={"msg": "Course not exist"}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         if request.method == "GET":
#             s = CourseSerializer(instance=course)
#             return Response(data=s.data, status=status.HTTP_200_OK)

#         elif request.method == "PUT":
#             s = CourseSerializer(instance=course, data=request.data, partial=True)
#             if s.is_valid():
#                 s.save()
#                 return Response(data=s.data, status=status.HTTP_200_OK)
#             return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

#         elif request.method == "DELETE":
#             course.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)


