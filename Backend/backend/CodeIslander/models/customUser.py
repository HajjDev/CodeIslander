from django.contrib.auth.models import AbstractUser
from django.db import models
from .exercise import Exercise
from .qcm import QCM
from .theory import Theory

class CustomUser(AbstractUser):
    emailChangeRequest = models.CharField(max_length=255, blank=True, null=True)
    vip = models.BooleanField(default=False)
    totpEnabled = models.BooleanField(default=False)
    unlockedExercises = models.ManyToManyField(Exercise, blank=True)
    unlockedQCM = models.ManyToManyField(QCM, blank=True)
    unlockedTheory = models.ManyToManyField(Theory, blank=True)
    secretTotp = models.CharField(default="")
    secretLogin = models.CharField(default='')