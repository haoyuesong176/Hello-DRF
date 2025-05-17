from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class MyUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="手机号")
    realname = models.CharField(max_length=50, blank=True, null=True, verbose_name="真实姓名")
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称")
    # icon = models.URLField(blank=True, null=True, verbose_name="头像URL")
    icon = models.ImageField(upload_to='user_icons/', blank=True, null=True, verbose_name="头像")
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

    class PaymentType(models.IntegerChoices):
        AVERAGE = 1, "平摊"
        PERSONAL = 2, "个人承担"

    date = models.DateField()
    time = models.TimeField()
    field_name = models.CharField(max_length=100)

    price = models.FloatField()

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    # booked Info

    booked_user_id = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_field_records'
    )

    booked_order_time = models.DateTimeField(null=True, blank=True)

    # matching Info

    matching_user_id = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matching_field_records'
    )

    matching_order_time = models.DateTimeField(null=True, blank=True)

    matching_min_level = models.DecimalField(
        max_digits=2,  # 总共最多两位，比如 5.0
        decimal_places=1,  # 保留一位小数
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0)
        ],
        null=True,
        blank=True
    )

    matching_payment_type = models.IntegerField(
        choices=PaymentType.choices,
        default=PaymentType.AVERAGE,
        null=True,
        blank=True
    )

    # matched Info

    matched_user_id = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matched_field_records'
    )

    matched_order_time = models.DateTimeField(null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=['date']),  # 为 date 建立索引
            models.Index(fields=['booked_user_id', 'status']),  # 复合索引
        ]

    def __str__(self):
        return f"{self.date} {self.time} {self.field_name}: {self.price}"