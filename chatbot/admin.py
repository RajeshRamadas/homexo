from django.contrib import admin
from .models import PropertyEmbedding, ChatSession, ChatMessage, UserProfile


@admin.register(PropertyEmbedding)
class PropertyEmbeddingAdmin(admin.ModelAdmin):
    list_display    = ('property', 'updated_at')
    readonly_fields = ('source_text', 'updated_at')
    search_fields   = ('property__title',)


class ChatMessageInline(admin.TabularInline):
    model           = ChatMessage
    extra           = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete      = False
    show_change_link = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    # ── Lead list view ────────────────────────────────────────────────────────────
    list_display    = ('visitor_name', 'phone', 'preference', 'message_count', 'created_at', 'updated_at')
    list_filter     = ('preference', 'created_at')
    search_fields   = ('visitor_name', 'phone', 'session_key')
    readonly_fields = ('session_key', 'created_at', 'updated_at')
    ordering        = ('-updated_at',)
    inlines         = [ChatMessageInline]

    @admin.display(description='Messages')
    def message_count(self, obj):
        return obj.messages.count()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display    = ('session_key', 'property_type', 'budget_min', 'budget_max', 'updated_at')
    search_fields   = ('session_key',)
    readonly_fields = ('session_key', 'updated_at')
