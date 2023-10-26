from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from post.models import Post, Comment
from chat.models import ChatMessage, ChatRoom, MessageReceiver
from django.utils.timesince import timesince
import json

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.change_message_status(self.scope['user'].username, self.room_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        # print('receiver', data)
        type = data.get('type')
        username = data.get('username')
        message = data.get('message')
        room = data.get('room')
        receivers = data.get('receivers')

        if type == 'mark_as_read':
            await self.channel_layer.group_send(
                self.room_group_name, {
                    'type': 'update_message_status',
                    'username': username,
                    'room': room,
                    'is_seen': data['is_seen'],
                }
            )

        if type == 'message' and message is not None:

            new_message = await self.save_message(username, room, message, receivers)

            await self.channel_layer.group_send(
                self.room_group_name, {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'room': room,
                    'timestamp': timesince(new_message.timestamp),
                    'receivers': receivers,
                }
            )

        elif type in ['typing', 'not-typing']:
            await self.channel_layer.group_send(
                self.room_group_name, {
                    'type': 'writing_active' if type == 'typing' else 'writing_inactive',
                    'message': message,
                    'username': username,
                    'room': room,
                }
            )

    async def update_message_status(self, event):
        # print('message status', event)
        username = event['username']
        room = event['room']
        is_seen = await self.change_message_status(username, room)
        await self.send(text_data=json.dumps({
            'username': username,
            'room': room,
            'is_seen': is_seen,

        }))

    async def chat_message(self, event):
        # print('chat_message', event)
        username = event['username']
        first_name, last_name = await self.get_first_name_and_last_name(username)
        participants_count = await self.get_participants_count(event['room'])

        await self.send(text_data=json.dumps({
            **event,
            'participants': participants_count,
            'first_name': first_name,
            'last_name': last_name,
        }))

    async def writing_active(self, event):
        username = event['username']
        first_name, last_name = await self.get_first_name_and_last_name(username)
        await self.send(text_data=json.dumps({
            **event,
            'first_name': first_name,
            'last_name': last_name,
        }))

    async def writing_inactive(self, event):
        await self.send(text_data=json.dumps({
            **event,
        }))

    @database_sync_to_async
    def save_message(self, username, room, message, receivers):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(slug=room)

        new_message = ChatMessage.objects.create(room=room, sender=user, message=message)
        receiver_users = User.objects.filter(username__in=receivers)
        new_message.receivers.set(receiver_users)

        for receiver in receiver_users:
            MessageReceiver.objects.create(message=new_message, receiver=receiver, is_seen=False)

        return new_message

    @database_sync_to_async
    def get_first_name_and_last_name(self, username):
        user = User.objects.get(username=username)
        return user.first_name, user.last_name

    @database_sync_to_async
    def get_participants_count(self, room_name):
        room_instance = ChatRoom.objects.get(slug=room_name)
        return room_instance.participants.count()

    @database_sync_to_async
    def change_message_status(self, username, room):
        user = User.objects.get(username=username)
        room_name = ChatRoom.objects.get(slug=room)
        if user in room_name.participants.all():
            message_receivers = MessageReceiver.objects.filter(message__room=room_name, receiver=user)
            for message_receiver in message_receivers:
                message_receiver.is_seen = True
                message_receiver.save()


class OnlineStatus(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = 'online_status'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        # print('receive', data)

        username = data['username']
        c_type = data['c_type']
        await self.change_online_status(username, c_type)
        # await self.channel_layer.group_send(
        #     self.room_group_name, {
        #         'type': 'send_status',
        #         'username': username,
        #         'is_online': is_online,
        #     }
        # )

    async def send_status(self, event):
        # print('send status', event)
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'is_online': event['is_online'],
        }))

    @database_sync_to_async
    def change_online_status(self, username, c_type):
        user = User.objects.get(username=username)
        if c_type == 'open':
            user.is_online = True
            user.save()
        else:
            user.is_online = False
            user.save()


class NotificationBadge(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'notification_badge'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # print('send notification', event)
        await self.send(text_data=json.dumps({
            'receiver': event['receiver'],
            'room': event['room'],
            'count': event['count'],
        }))

    async def send_create_chatroom(self, event):
        # print('send create chatroom', event)
        await self.send(text_data=json.dumps({
            **event,
        }))


class PostLike(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'post_like'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        # print('receiver post like', data)
        username = data.get('username')
        post = data.get('post')
        like, user_liked, likers = await self.post_like(username, post)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_post_like',
                'username': username,
                'post': post,
                'like': like,
                'user_liked': user_liked,
                'likers': likers,
            }
        )

    async def send_post_like(self, event):
        # print('send post like', event)
        await self.send(text_data=json.dumps({
            **event,
        }))

    @database_sync_to_async
    def post_like(self, username, slug):
        user = User.objects.get(username=username)
        post_name = Post.objects.get(slug=slug)
        if user in post_name.like.all():
            post_name.like.remove(user)
            post_name.save()
            like_users = list(post_name.like.values_list('username', flat=True))
            return post_name.like.count(), False, like_users
        else:
            post_name.like.add(user)
            post_name.save()
            like_users = list(post_name.like.values_list('username', flat=True))
            return post_name.like.count(), True, like_users


class PostComment(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'post_comment'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        # print('receiver post like', data)
        username = data.get('username')
        post = data.get('post')
        content = data.get('content')
        comment_id = data.get('comment_id')
        type = data.get('type')

        if type == 'create_comment':
            new_comment, new_comment_id, user_post = await self.save_post_comment(username, post, content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_post_comment',
                    'username': username,
                    'post': post,
                    'content': content,
                    'created_at': timesince(new_comment.created_at),
                    'comment_id': new_comment_id,
                    'user_post': user_post,
                }
            )

        if type == 'delete_comment':
            await self.delete_post_comment(username, post, comment_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_delete_post_comment',
                    'username': username,
                    'post': post,
                    'comment_id': comment_id,
                }
            )

        if type == 'edit_comment':
            edit_comment, created_at = await self.edit_post_comment(username, comment_id, content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_edit_post_comment',
                    'username': username,
                    'post': post,
                    'content': content,
                    'comment_id': comment_id,
                    'created_at': created_at.strftime("%B %d, %Y - %H:%M"),
                }
            )

    async def send_post_comment(self, event):
        # print('send post comment', event)
        photo = await self.get_user_photo(event['username'])
        await self.send(text_data=json.dumps({
            **event,
            'photo': photo
        }))

    async def send_delete_post_comment(self, event):
        # print('delete post comment', event)
        await self.send(text_data=json.dumps({
            **event,
        }))

    async def send_edit_post_comment(self, event):
        # print('edit post comment', event)
        photo = await self.get_user_photo(event['username'])

        await self.send(text_data=json.dumps({
            **event,
            'photo': photo
        }))

    @database_sync_to_async
    def save_post_comment(self, username, slug, comment):
        user = User.objects.get(username=username)
        post = Post.objects.get(slug=slug)
        content = Comment.objects.create(user=user, post=post, content=comment)
        return content, content.id, post.user.username

    @database_sync_to_async
    def delete_post_comment(self, username, slug, id):
        user = User.objects.get(username=username)
        post = Post.objects.get(slug=slug)
        comment = Comment.objects.get(id=id)
        if comment.user == user or post.user == user:
            comment.delete()

    @database_sync_to_async
    def edit_post_comment(self, username, id, new_comment):
        user = User.objects.get(username=username)
        old_comment = Comment.objects.get(id=id)
        if old_comment.user == user:
            old_comment.content = new_comment
            old_comment.save()
            return old_comment, old_comment.created_at

    @database_sync_to_async
    def get_user_photo(self, username):
        user = User.objects.get(username=username)
        return user.photo.url
