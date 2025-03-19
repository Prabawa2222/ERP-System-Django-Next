from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("employee", "Employee"),
        ("accountant", "Accountant"),
    )

    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="employee"
    )
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username
