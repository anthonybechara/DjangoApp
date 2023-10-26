from django.urls import path

from .views import chatroom, create_chat, chats

app_name = 'chat'

urlpatterns = [
    path('chats/', chats, name='chats'),
    path('chatroom/<slug:slug>/', chatroom, name='chatroom'),
    path('chats/create/', create_chat, name='create-chat'),

]
