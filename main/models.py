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
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=10)
    frequency = models.PositiveIntegerField()
    hymn = models.BooleanField()
    scheduled = models.DateField(null=True, blank=True)
    last_scheduled = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Logs(models.Model):
    user = models.CharField(max_length=20)
    action = models.CharField(max_length=150)
    date_of_action = models.DateField(default=timezone.now())

    obj_name = models.CharField(max_length=50, default="No Name")
    