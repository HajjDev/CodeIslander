from django.db import models
from .exercise import Exercise

class Tests(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="tests")
    name = models.CharField(max_length=200, default="")
    test_type = models.CharField(max_length=50)
    inputs = models.JSONField(
        blank=True,
        null=True
    )
    stdin_data = models.TextField(
        blank=True,
        null=True
    )
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.exercise_id.title} - {self.name}"