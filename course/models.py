from django.db import models
from django.conf import settings
from django.contrib.auth.models import User 

# class Course(models.Model):
#     name = models.CharField(max_length=255, unique=True, help_text='课程名称', verbose_name='名称')
#     introduction = models.TextField(help_text='课程简介', verbose_name='简介')
#     teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='课程讲师', verbose_name='讲师')
#     price = models.DecimalField(max_digits=6, decimal_places=2, help_text='课程价格', verbose_name='价格')
#     created_at = models.DateTimeField(auto_now=True, verbose_name='创建时间')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

#     class Meta:
#         verbose_name = '课程信息'
#         verbose_name_plural = verbose_name
#         ordering = ('price',)

#     def __str__(self):
#         return self.name
    

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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='field_records'
    )

    booked_order_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),  # 为 date 建立索引
        ]

    def __str__(self):
        return f"{self.date} {self.time} {self.field_name}: {self.price}"