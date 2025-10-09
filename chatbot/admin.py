from django.contrib import admin
from .models import Conversation, Message, KnowledgeBase

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['question_type', 'question_pattern', 'keywords']
    list_filter = ['question_type']
    search_fields = ['question_pattern', 'keywords', 'answer']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'session_key', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['title']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'content_preview', 'is_user', 'timestamp']
    list_filter = ['is_user', 'timestamp']
    search_fields = ['content']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'