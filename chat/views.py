import uuid
from django.db.models import Count, Max
from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatRoom, ChatMessage, MessageReceiver
from .forms import CreateChatRoomForm
from django.contrib.auth.decorators import login_required
from django.db import models

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@login_required
def chats(request):
    chat_room = ChatRoom.objects.all()
    current_user = request.user
    chat_rooms = ChatRoom.objects.filter(participants=current_user).annotate(
        latest_message=Max('chatmessage__timestamp')).order_by('-latest_message')
    # chat_rooms = chat_rooms.annotate(
    #     priority_order=Case(
    #         When(chatmessage__isnull=True, then=Value(1)),
    #         default=Value(0),
    #         output_field=models.IntegerField()
    #     )
    # )
    #
    # chat_rooms = chat_rooms.order_by('-priority_order', '-latest_message')
    room_message_unseen = MessageReceiver.objects.filter(receiver=current_user, is_seen=False).values(
        'message__room_id') \
        .annotate(nbr=Count('receiver'))
    return render(request, 'chat/chats.html',
                  {'chatroom': chat_room, 'chat_rooms': chat_rooms, 'room_message_unseen': room_message_unseen})


@login_required
def chatroom(request, slug):
    chat_room = get_object_or_404(ChatRoom, slug=slug)
    messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    current_user = request.user
    chat_rooms = ChatRoom.objects.filter(participants=current_user).annotate(
        latest_message=Max('chatmessage__timestamp')).order_by('-latest_message')
    participants = chat_room.participants.all()
    room_message_unseen = MessageReceiver.objects.filter(receiver=current_user, is_seen=False).values(
        'message__room_id') \
        .annotate(nbr=Count('receiver'))

    return render(request, 'chat/chat_room.html',
                  {'chatroom': chat_room, 'messages': messages, 'chat_rooms': chat_rooms,
                   'participants': participants, 'room_message_unseen': room_message_unseen})


@login_required
def create_chat(request):
    current_user = request.user

    if request.method == 'POST':
        form = CreateChatRoomForm(request.POST, current_user=current_user)
        if form.is_valid():
            selected_participants = form.cleaned_data['participants']

            # Include the current user in the participants list
            sorted_participants = sorted([current_user] + list(selected_participants), key=lambda user: user.username)

            # Get chat rooms with the same number of participants
            existing_chat_rooms = ChatRoom.objects.annotate(participant_count=models.Count('participants')).filter(
                participant_count=len(sorted_participants))

            # Filter further to ensure all participants match the sorted list
            for participant in sorted_participants:
                existing_chat_rooms = existing_chat_rooms.filter(participants=participant)

            if existing_chat_rooms.exists():
                # Redirect to the existing chat room
                return redirect('chatroom', slug=existing_chat_rooms.first().slug)

            # If no existing chat room, create a new one
            slug = str(uuid.uuid4())
            chat_room = ChatRoom.objects.create(slug=slug)
            chat_room.participants.set(sorted_participants)

            participant_info = []
            for participant in sorted_participants:
                participant_info.append({
                    'username': participant.username,
                    'first_name': participant.first_name,
                    'last_name': participant.last_name,
                    'photo': participant.photo.url,

                })

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'notification_badge',
                {
                    'type': 'send_create_chatroom',
                    'participants': participant_info,
                    'room': chat_room.slug,
                    'created': True,
                }
            )

            return redirect('chat:chatroom', slug=chat_room.slug)
    else:
        form = CreateChatRoomForm(current_user=current_user)

    return render(request, 'chat/create_chat.html', {'form': form})
