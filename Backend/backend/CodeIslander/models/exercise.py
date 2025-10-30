from django.db import models

class Exercise(models.Model):
    title = models.CharField(default="", max_length=200)
    subject = models.CharField(default="")
    example = models.CharField(default="",blank=True, null=True)
    hints = models.CharField(default="", blank=True, null=True)
    test_file = models.CharField(default="")
    prompt = models.CharField(default="", blank=True, null=True)
    solution = models.CharField(default="",blank=True, null=True)
    
    def __str__(self):
        return self.title