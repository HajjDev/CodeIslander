from django.db import models

class Exercise(models.Model):
    title = models.CharField(default="", max_length=200)
    subject = models.CharField(default="")
    example = models.CharField(default="")
    hints = models.CharField(default="")
    test_file = models.CharField(default="")
    
    def __str__(self):
        return self.title