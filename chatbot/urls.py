from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/conversation/<int:conversation_id>/', views.conversation_history, name='conversation_history'),
    path('api/conversations/', views.list_conversations, name='list_conversations'),
]
