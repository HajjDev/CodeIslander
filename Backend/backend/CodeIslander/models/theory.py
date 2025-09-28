from django.db import models
from .exercise import Exercise

class Theory(models.Model):
    title = models.CharField(default = '', max_length=200)
    content = models.CharField(default= '')
    example = models.CharField(default= '', null=True, blank=True)
    exercisesUnlocked = models.ManyToManyField(Exercise, blank=True)

    def __str__(self):
        return self.title