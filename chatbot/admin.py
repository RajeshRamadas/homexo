from django.contrib import admin
from .models import PropertyEmbedding, ChatSession, ChatMessage


@admin.register(PropertyEmbedding)
class PropertyEmbeddingAdmin(admin.ModelAdmin):
    list_display  = ('property', 'updated_at')
    readonly_fields = ('source_text', 'updated_at')
    search_fields = ('property__title',)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display  = ('session_key', 'user', 'created_at', 'updated_at')
    inlines       = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('session_key', 'user__email')
