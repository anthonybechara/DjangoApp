from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='received_messages')

    def __str__(self):
        return self.sender.username


class MessageReceiver(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.receiver.username
