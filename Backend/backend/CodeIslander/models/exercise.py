from django.db import models

class Exercise(models.Model):
    title = models.CharField(default="", max_length=200)
    subject = models.TextField(default="")
    example = models.TextField(default="", blank=True, null=True)
    hints = models.TextField(default="", blank=True, null=True)
    prompt = models.TextField(default="", blank=True, null=True)
    
    setup_code = models.TextField(
        default="", 
        blank=True,
        help_text="Hidden code to run BEFORE the user's code (e.g., variable definitions)"
    )
    
    setup_files = models.JSONField(
        default=dict, 
        blank=True,
        null=True,
        help_text='JSON object of setup files: {"filename.txt": "content"}'
    )

    function_to_test = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Name of the function to test (e.g., 'add'). Leave blank for stdin/stdout programs."
    )
    
    module_name = models.CharField(
        max_length=100, 
        default='user_code',
        help_text="The module name to import. Default is 'user_code'."
    )
    
    def __str__(self):
        return self.title