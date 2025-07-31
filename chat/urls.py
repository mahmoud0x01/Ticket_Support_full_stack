from django.urls import path
from . import views

urlpatterns = [
    path('<int:ticket_id>/', views.chat_room, name='chat_room'),
    path('tickets/<int:ticket_id>/messages/', views.MessageListCreate.as_view(), name='messages'),
    path('tickets/<int:ticket_id>/mark-read/', views.mark_messages_read, name='mark-read'),
    # Add your existing URL patterns here
    path('test-websocket/<int:ticket_id>/', views.test_websocket_url, name='test_websocket_url'),
]