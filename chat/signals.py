from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.models import MessageReceiver, ChatRoom

User = get_user_model()


@receiver(post_save, sender=User)
def send_status(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        user = instance.username
        user_status = instance.is_online

        async_to_sync(channel_layer.group_send)(
            'online_status', {
                'type': 'send_status',
                'username': user,
                'is_online': user_status,
            }
        )


@receiver(post_save, sender=MessageReceiver)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        user = instance.receiver
        room = instance.message.room

        message_seen = MessageReceiver.objects.filter(message__room=room, receiver=user, is_seen=False).count()

        async_to_sync(channel_layer.group_send)(
            'notification_badge', {
                'type': 'send_notification',
                'receiver': user.username,
                'room': room.slug,
                'count': message_seen,
            }
        )

# @receiver(post_save, sender=ChatRoom)
# async def send_create_chatroom(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         participants = [user.username for user in instance.participants.all()]
#         room = instance.slug
#
#         await asyncio.gather(
#             channel_layer.group_send(
#                 'create_chatroom', {
#                     'type': 'send_create_chatroom',
#                     'participants': participants,
#                     'room': room,
#                 }
#             )
#         )
