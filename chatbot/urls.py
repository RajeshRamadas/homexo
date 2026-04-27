from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/',               views.chat_view,               name='chat'),
    path('chat/preferences/',   views.update_preferences_view, name='preferences'),
]
