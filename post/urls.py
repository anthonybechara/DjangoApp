from django.urls import path

from .views import CreatePost, HomeView, MyPosts, DeletePost, UpdatePost

app_name = 'post'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('myposts/', MyPosts.as_view(), name='my-posts'),

    path('myposts/create/', CreatePost.as_view(), name='create-post'),

    path('myposts/<slug:slug>/delete/', DeletePost.as_view(), name='delete-post'),

    path('myposts/<slug:slug>/update/', UpdatePost.as_view(), name='edit-post'),

    # FOR METHOD 1 & 2
    # path('home/<int:pk>', CommentView.as_view(), name='create-comment'),
    # FOR METHOD 3
    # path('home/<int:pk>', HomeView.as_view(), name='comment-create'),
    # path('home/<int:pk>/edit/', UpdateComment.as_view(), name='edit-comment'),
    # path('home/<int:pk>/delete', DeleteComment.as_view(), name='delete-comment'),
]
