from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="手机号")
    realname = models.CharField(max_length=50, blank=True, null=True, verbose_name="真实姓名")
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称")
    icon = models.URLField(blank=True, null=True, verbose_name="头像URL")
    level = models.DecimalField(max_digits=3, decimal_places=1, default=1.0,
                                verbose_name="网球水平等级", help_text="范围：1.0 - 5.0")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="账户余额")
    session_key = models.CharField(max_length=50, blank=True, null=True, verbose_name="session_key")
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class FieldRecord(models.Model):
    class Status(models.IntegerChoices):
        AVAILABLE = 1, 'Available'
        BOOKED = 2, 'Booked'
        MATCHING = 3, 'Matching'
        MATCHED = 4, 'Matched'

    date = models.DateField()
    time = models.TimeField()
    field_name = models.CharField(max_length=100)

    price = models.FloatField()

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    booked_user_id = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='field_records'
    )

    booked_order_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),  # 为 date 建立索引
            models.Index(fields=['booked_user_id', 'status']),  # 复合索引
        ]

    def __str__(self):
        return f"{self.date} {self.time} {self.field_name}: {self.price}"