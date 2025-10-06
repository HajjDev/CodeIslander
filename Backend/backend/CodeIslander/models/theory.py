from django.db import models
from .exercise import Exercise

class Theory(models.Model):
    title = models.CharField(max_length=200, default='')
    content = models.TextField(default='')
    exercisesUnlocked = models.ManyToManyField(Exercise, blank=True)

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
from django.db import models
from .theory import Theory  # adjust import according to your app structure

class Table(models.Model):
    theory = models.ForeignKey(Theory, on_delete=models.CASCADE, related_name='tables')
    number = models.PositiveIntegerField()  # e.g. [[table:1]], [[table:2]]
    title = models.CharField(max_length=200, blank=True)
    csv_content = models.TextField()  # store CSV text here

    class Meta:
        unique_together = ('theory', 'number')  # ensures no duplicate table numbers per theory

    def __str__(self):
        return f"Table {self.number} for {self.theory.title}"
