from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    emailChangeRequest = models.CharField(max_length=255, blank=True, null=True)
    vip = models.BooleanField()
    totpEnabled = models.BooleanField()