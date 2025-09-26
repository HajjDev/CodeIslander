from django.db import models

class Theory(models.Model):
    title = models.CharField(default = '', max_length=200)
    content = models.CharField(default= '')
    example = models.CharField(default= '')


    def __str__(self):
        return self.title