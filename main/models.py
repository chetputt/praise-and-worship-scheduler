from django.db import models
from django.utils import timezone

# Create your models here.
class Schedule(models.Model):
    date = models.DateField(default=timezone.now)
    songs = models.ManyToManyField("Song")
    
    def __str__(self):
        return self.name
    

class Song(models.Model):
    #schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=4)
    frequency = models.PositiveIntegerField()
    hymn = models.BooleanField()

    def __str__(self):
        return self.name