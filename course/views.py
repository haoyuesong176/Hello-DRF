from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import FieldRecord, MyUser
from .serializers import FieldRecordSerializer
from collections import defaultdict
from datetime import date, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
import requests
import json

class WXLoginView(APIView):

    authentication_classes = []  # 不需要认证
    permission_classes = [AllowAny]  # 所有人可访问

    def post(self, request):
        code = request.data.get('code')
        print(code)
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
        user, created = MyUser.objects.get_or_create(openid=openid)

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


class FieldRecordList(APIView):

    def get(self, request):
        queryset = FieldRecord.objects.all()
        s = FieldRecordSerializer(instance=queryset, many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)

    def post(self, request):
        s = FieldRecordSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldRecordDetail(APIView):

    @staticmethod
    def get_record(pk):
        try:
            return FieldRecord.objects.get(pk=pk)
        except FieldRecord.DoesNotExist:
            return None 

    def get(self, request, pk):
        obj = self.get_record(pk)
        if obj:
            s = FieldRecordSerializer(instance=obj)
            return Response(data=s.data, status=status.HTTP_200_OK)
        return Response(data={"msg": "Record not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        obj = self.get_record(pk)
        if obj:
            s = FieldRecordSerializer(instance=obj, data=request.data, partial=True)
            if s.is_valid():
                s.save()
                return Response(data=s.data, status=status.HTTP_200_OK)
            else:
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"msg": "Record not exist"}, status=status.HTTP_404_NOT_FOUND)
