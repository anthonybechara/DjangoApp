import uuid
from django.db import models
from django.conf import settings


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='post/%y/%m/%d', )
    caption = models.CharField(max_length=200, null=True)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='posts_like', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.caption


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
