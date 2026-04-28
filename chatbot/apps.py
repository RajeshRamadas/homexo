from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name  = 'chatbot'
    label = 'chatbot'
    verbose_name = 'AI Chatbot'

    def ready(self):
        import chatbot.signals  # noqa: F401 — registers post_save/post_delete signals
