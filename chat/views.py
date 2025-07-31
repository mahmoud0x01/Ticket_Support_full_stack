from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Message
from .serializers import MessageSerializer
from tickets.models import Ticket
from tickets.views import IsOwnerOrSupport
from django.shortcuts import render
from django.http import JsonResponse

class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSupport]

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return Message.objects.filter(ticket_id=ticket_id)

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        ticket = Ticket.objects.get(id=ticket_id)
        serializer.save(sender=self.request.user, ticket=ticket)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsOwnerOrSupport])
def mark_messages_read(request, ticket_id):
    # Mark all messages in the ticket as read for the current user
    messages = Message.objects.filter(ticket_id=ticket_id).exclude(sender=request.user)
    messages.update(is_read=True)
    return Response({'status': 'Messages marked as read'})

def chat_room(request, ticket_id):
    return render(request, 'chat/room.html', {
        'ticket_id': ticket_id
    })

def test_websocket_url(request, ticket_id):
    """A simple view to test if the WebSocket URL is correctly configured."""
    return JsonResponse({
        'message': 'WebSocket URL is correctly configured',
        'websocket_url': f'ws://{request.get_host()}/ws/chat/{ticket_id}/'
    })