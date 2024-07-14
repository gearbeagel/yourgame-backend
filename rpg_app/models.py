from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Story(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Character(models.Model):
    name = models.CharField(max_length=100)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='characters')
    description = models.TextField()

    def __str__(self):
        return self.name


class Setting(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='settings')

    def __str__(self):
        return self.name


class Plot(models.Model):
    title = models.CharField(max_length=100)
    summary = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='plots')

    def __str__(self):
        return self.title
