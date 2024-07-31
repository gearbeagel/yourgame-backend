from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.
class Story(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Character(models.Model):
    description = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='characters')

    def __str__(self):
        return self.description


class Setting(models.Model):
    description = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='settings')

    def __str__(self):
        return self.description


class Plot(models.Model):
    summary = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='plots')

    def __str__(self):
        return self.summary


class ChatLog(models.Model):
    title = models.CharField(max_length=100)
    story = models.ForeignKey('Story', related_name='chat_logs', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message_data = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ChatLog for {self.story.title} at {self.timestamp}"
