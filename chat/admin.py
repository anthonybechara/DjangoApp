from django.contrib import admin
from .models import ChatMessage, ChatRoom, MessageReceiver


class CustomRoom(admin.ModelAdmin):
    list_display = ('slug',)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message', 'timestamp')
    readonly_fields = ('timestamp',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sender":
            # Get the selected ChatRoom if available
            chat_room_id = request.POST.get('room') or request.GET.get('room')
            if chat_room_id:
                chat_room = ChatRoom.objects.get(pk=chat_room_id)
                kwargs["queryset"] = chat_room.participants.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(ChatRoom, CustomRoom)
admin.site.register(ChatMessage, ChatMessageAdmin)


class CustomMessageReceiver(admin.ModelAdmin):
    list_display = ('get_sender', 'get_message', 'receiver', 'is_seen')

    def get_sender(self, obj):
        return obj.message.sender.username

    get_sender.short_description = 'Sender'

    def get_message(self, obj):
        return obj.message.message

    get_message.short_description = 'Message'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "receiver":
            message_id = request.POST.get('message') or request.GET.get('message')
            if message_id:
                message = ChatMessage.objects.get(pk=message_id)
                kwargs["queryset"] = message.receivers.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(MessageReceiver, CustomMessageReceiver)
