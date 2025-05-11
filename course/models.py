from django.db import models
from django.conf import settings
from django.contrib.auth.models import User 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, openid):
        user = self.model(openid=openid)
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser):
    openid = models.CharField(max_length=64, unique=True)
    USERNAME_FIELD = 'openid'
    objects = UserManager()

    def __str__(self):
        return self.openid
        

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