from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import FieldRecord, MyUser
from .serializers import *
from collections import defaultdict
from datetime import date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Q
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
                'nickname': '匿名用户',
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
    

class BookFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

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


class UserMatchingFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = request.user

        # 查询当前用户所有 status=3（MATCHING）的 FieldRecord
        records = FieldRecord.objects.filter(
            matching_user_id=current_user,
            status=FieldRecord.Status.MATCHING
        )

        # 序列化数据
        serializer = FieldRecordSerializerMatching(records, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserMatchedFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = request.user

        records = FieldRecord.objects.filter(
            status=FieldRecord.Status.MATCHED,
            matching_user_id=current_user
        ).union(
            FieldRecord.objects.filter(
                status=FieldRecord.Status.MATCHED,
                matched_user_id=current_user
            )
        )

        serializer = FieldRecordSerializerMatched(records, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


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
    

class UnmatchingFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FieldRecordUnmatchSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_list = serializer.validated_data['id_list']

        # 过滤出状态为 MATCHING 的记录
        records = FieldRecord.objects.filter(
            id__in=id_list,
            status=FieldRecord.Status.MATCHING
        )

        # 更新状态为 AVAILABLE，并清空 matching 字段
        records.update(
            status=FieldRecord.Status.AVAILABLE,
            matching_user_id=None,
            matching_order_time=None,
            matching_min_level=None,
            matching_payment_type=None,
        )

        return Response({
            "message": "Selected field records have been successfully un-matched and set to available.",
            "unmatched_ids": list(records.values_list('id', flat=True))
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # 必须登录才能访问

    def get(self, request, *args, **kwargs):
        user = request.user  # 获取当前登录用户
        serializer = MyUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserIconView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):  # 改为支持 POST
        user = request.user
        icon_file = request.data.get('icon')

        if not icon_file:
            return Response({"error": "No icon file provided."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MyUserSerializer(user, data={'icon': icon_file}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FieldRecordMatchingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_list = serializer.validated_data['id_list']
        payment_type = serializer.validated_data['payment_type']
        min_level = serializer.validated_data['min_level']

        current_user = request.user

        # 更新状态与匹配相关字段
        FieldRecord.objects.filter(id__in=id_list).update(
            status=FieldRecord.Status.MATCHING,
            matching_user_id=current_user.id,
            matching_order_time=timezone.now(),
            matching_min_level=min_level,
            matching_payment_type=payment_type
        )

        return Response({
            "message": "Successfully updated records for matching.",
            "matched_ids": id_list
        }, status=status.HTTP_200_OK)
    

class FieldMatchingUserInfoView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, field_id, *args, **kwargs):
        try:
            field_record = FieldRecord.objects.get(id=field_id)
        except FieldRecord.DoesNotExist:
            return Response(
                {"error": "FieldRecord not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if field_record.status != field_record.Status.MATCHING:
            return Response(
                {"error": "The current status is not MATCHING."},
                status=status.HTTP_400_BAD_REQUEST
            )

        matching_user = field_record.matching_user_id
        if not matching_user:
            return Response(
                {"error": "No matching user associated with this field record."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MatchingUserInfoSerializer(matching_user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfirmMatchFieldRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ConfirmMatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_list = serializer.validated_data['id_list']
        current_user = request.user

        updated_count = FieldRecord.objects.filter(id__in=id_list).update(
            status=FieldRecord.Status.MATCHED,
            matched_user_id=current_user.id,
            matched_order_time=timezone.now()
        )

        return Response({
            "message": f"Successfully marked {updated_count} records as matched.",
            "matched_ids": id_list
        }, status=status.HTTP_200_OK)
    

class UserTodayScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = date.today()
        user = request.user

        # 查询今日与当前用户相关的日程记录
        records = FieldRecord.objects.filter(
            Q(booked_user_id=user) | Q(matching_user_id=user) | Q(matched_user_id=user),
            date=today
        ).order_by('time')

        serializer = FieldRecordScheduleSerializer(records, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)