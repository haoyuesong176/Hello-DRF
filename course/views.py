from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import FieldRecord, MyUser
from .serializers import FieldRecordSerializer, FieldRecordBookingSerializer, FieldRecordUnbookSerializer, MyUserSerializer
from collections import defaultdict
from datetime import date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import requests
import json

class WXLoginView(APIView):

    authentication_classes = []  # 不需要认证
    permission_classes = [AllowAny]  # 所有人可访问
    

    def post(self, request):
        code = request.data.get('code')
        wx_url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            'appid': 'wx25922ebd6daf6d3c',
            'secret': 'c9ec850e6dab5a66f1f819d977e18ee5',
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        wx_resp = requests.get(wx_url, params=params).json()
        openid = wx_resp.get('openid')
        session_key = wx_resp.get('session_key')

        if not openid:
            return Response({'error': '登录失败'}, status=400)

        # 查找或创建用户
        user, created = MyUser.objects.get_or_create(
            username=openid,
            defaults={
                'username': openid,
                # 可选：设置其他默认字段，如：
                # 'level': 1.0,
                # 'balance': 0.00
            }
        )

        user.session_key = session_key
        user.save(update_fields=['session_key'])  # 更高效地只更新该字段

        # 签发 JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'openid': openid
        })


class FieldDictView(APIView):
    def get(self, request):
        # 获取请求中的日期参数（格式应为 YYYY-MM-DD）
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response({"error": "缺少日期参数，请提供 date=YYYY-MM-DD"}, status=400)

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({"error": "日期格式错误，请使用 YYYY-MM-DD"}, status=400)

        # 数据库层：仅查询指定日期的数据
        queryset = FieldRecord.objects.filter(date=target_date)

        FieldDict = defaultdict(lambda: defaultdict(dict))

        for record in queryset:
            serializer = FieldRecordSerializer(record)
            data = serializer.data

            time_str = record.time.strftime('%H:%M')

            FieldDict[time_str][record.field_name] = data

        return Response(FieldDict)


# class FieldRecordList(APIView):

#     authentication_classes = []  # 不需要认证
#     # permission_classes = [AllowAny]  # 所有人可访问

#     def get(self, request):
#         queryset = FieldRecord.objects.all()
#         s = FieldRecordSerializer(instance=queryset, many=True)
#         return Response(data=s.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         s = FieldRecordSerializer(data=request.data)
#         if s.is_valid():
#             s.save()
#             return Response(data=s.data, status=status.HTTP_201_CREATED)
#         return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


# class FieldRecordDetail(APIView):

#     @staticmethod
#     def get_record(pk):
#         try:
#             return FieldRecord.objects.get(pk=pk)
#         except FieldRecord.DoesNotExist:
#             return None 

#     def get(self, request, pk):
#         obj = self.get_record(pk)
#         if obj:
#             s = FieldRecordSerializer(instance=obj)
#             return Response(data=s.data, status=status.HTTP_200_OK)
#         return Response(data={"msg": "Record not exist"}, status=status.HTTP_404_NOT_FOUND)

#     def put(self, request, pk):
#         obj = self.get_record(pk)
#         if obj:
#             s = FieldRecordSerializer(instance=obj, data=request.data, partial=True)
#             if s.is_valid():
#                 s.save()
#                 return Response(data=s.data, status=status.HTTP_200_OK)
#             else:
#                 return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(data={"msg": "Record not exist"}, status=status.HTTP_404_NOT_FOUND)
    

class BookFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = []
    # permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = FieldRecordBookingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_list = serializer.validated_data['id_list']

        current_user = request.user

        # 更新状态、用户、下单时间
        FieldRecord.objects.filter(id__in=id_list).update(
            status=FieldRecord.Status.BOOKED,
            booked_user_id=current_user.id,
            booked_order_time=timezone.now()
        )

        return Response({
            "message": "Successfully booked the selected field records.",
            "booked_ids": id_list
        }, status=status.HTTP_200_OK)

# TODO
class UserBookedFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = request.user

        # 查询当前用户所有已预订（status=2）的 FieldRecord
        records = FieldRecord.objects.filter(
            booked_user_id=current_user,
            status=FieldRecord.Status.BOOKED
        )

        # 序列化数据
        serializer = FieldRecordSerializer(records, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# TODO
class UnbookFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FieldRecordUnbookSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_list = serializer.validated_data['id_list']

        # 更新状态为 AVAILABLE，并清空预订信息
        FieldRecord.objects.filter(id__in=id_list).update(
            status=FieldRecord.Status.AVAILABLE,
            booked_user_id=None,
            booked_order_time=None
        )

        return Response({
            "message": "Selected field records have been successfully unbooked.",
            "unbooked_ids": id_list
        }, status=status.HTTP_200_OK)


# TODO
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # 必须登录才能访问

    def get(self, request, *args, **kwargs):
        user = request.user  # 获取当前登录用户
        serializer = MyUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
