from django.db import models

class Exercise(models.Model):
    title = models.CharField(default="", max_length=200)
    subject = models.CharField(default="")
    example = models.CharField(default="",blank=True, null=True)
    hints = models.CharField(default="", blank=True, null=True)
    prompt = models.CharField(default="", blank=True, null=True)
    solution = models.CharField(default="",blank=True, null=True)

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