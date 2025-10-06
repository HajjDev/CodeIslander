from django.db import models

class Theory(models.Model):
    title = models.CharField(max_length=200, default='')
    content = models.TextField(default='')

    def __str__(self):
        return self.title


class Example(models.Model):
    theory = models.ForeignKey(Theory, on_delete=models.CASCADE, related_name='examples')
    number = models.PositiveIntegerField()  # e.g. [[example:1]], [[example:2]]
    content = models.TextField()

    class Meta:
        unique_together = ('theory', 'number')  # ensures no duplicate numbers per theory

    def __str__(self):
        return f"Example {self.number} for {self.theory.title}"
