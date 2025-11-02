from django.db import models

class Exercise(models.Model):
    title = models.CharField(default="", max_length=200)
    subject = models.TextField(default="") # Use TextField for longer subjects
    example = models.TextField(default="", blank=True, null=True) # TextField is better
    hints = models.TextField(default="", blank=True, null=True)   # TextField is better
    prompt = models.TextField(default="", blank=True, null=True)  # TextField is better

    function_to_test = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
    )
    
    module_name = models.CharField(
        max_length=100, 
        default='user_code',
    )
    
    def __str__(self):
        return self.title