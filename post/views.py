from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView, DeleteView, UpdateView
from .forms import PostForm, CommentForm
from .models import Post, Comment


# METHOD 1
class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post/index.html'
    paginate_by = 4
    ordering = ['-created']

# Used instead of Websocket
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CommentForm()
#         return context
#
#
# class CommentView(LoginRequiredMixin, CreateView):
#     model = Comment
#     form_class = CommentForm
#     success_url = reverse_lazy('index')
#
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         form.instance.post_id = self.kwargs['pk']
#         return super().form_valid(form)


# METHOD 2
# class HomeView(LoginRequiredMixin, ListView):
#     model = Post
#     template_name = 'post/index.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CommentForm()
#         return context
#
#
# class CommentView(LoginRequiredMixin, FormView):
#     model = Comment
#     form_class = CommentForm
#
#     def post(self, request, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.user = self.request.user
#             comment.post_id = self.kwargs['pk']
#             comment.save()
#             return redirect('home')

# METHOD 3
# class HomeView(LoginRequiredMixin, CreateView, ListView):
#     model = Post
#     form_class = CommentForm
#     template_name = 'post/index.html'
#     context_object_name = 'post_list'
#     success_url = reverse_lazy('home')
#
#     def get_queryset(self):
#         # Override the queryset to order posts by their creation date in descending order
#         return Post.objects.order_by('-created')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = self.form_class()  # Add an empty form for comment creation
#         return context
#
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         form.instance.post_id = self.kwargs['pk']
#         return super().form_valid(form)


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post/create_post.html'
    success_url = reverse_lazy('post:home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MyPosts(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post/my_posts.html'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-created')


class DeletePost(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post/delete_post.html'
    success_url = reverse_lazy('post:my-posts')


class UpdatePost(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post/update_post.html'
    success_url = reverse_lazy('my-posts')

# Used instead of websocket
# class UpdateComment(LoginRequiredMixin, UpdateView):
#     model = Comment
#     form_class = CommentForm
#     success_url = reverse_lazy('index')
#
#
# class DeleteComment(LoginRequiredMixin, DeleteView):
#     model = Comment
#     success_url = reverse_lazy('index')
