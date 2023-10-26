from django.contrib import admin

from .models import Post, Comment


class CustomPost(admin.ModelAdmin):
    readonly_fields = ('created',)
    list_display = ('user', 'caption')


class CustomComment(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    list_display = ('user', 'post', 'comment')

    def comment(self, obj):
        return "".join(obj.content)

    comment.short_description = 'Comment'


admin.site.register(Post, CustomPost)
admin.site.register(Comment, CustomComment)
