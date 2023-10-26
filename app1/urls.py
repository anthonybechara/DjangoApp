from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from two_factor.urls import urlpatterns as tf_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('', include('user_sessions.urls', 'user_sessions')),
    path('', include(tf_urls)),
    path('', include('post.urls')),
    path('', include('chat.urls')),

]

urlpatterns += [
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
