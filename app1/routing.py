from django.urls import path
from app1 import consumers

websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/user/online/', consumers.OnlineStatus.as_asgi()),
    path('ws/user/notification/', consumers.NotificationBadge.as_asgi()),
    path('ws/post/like/', consumers.PostLike.as_asgi()),
    path('ws/post/comment/', consumers.PostComment.as_asgi()),
]
