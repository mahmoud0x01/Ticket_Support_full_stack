import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from .models import Message

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'chat_{self.ticket_id}'
        
        logger.info(f"WebSocket connect attempt for ticket_id: {self.ticket_id}")
        print(f"WebSocket connect attempt for ticket_id: {self.ticket_id}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f"WebSocket connected for ticket_id: {self.ticket_id}")
        print(f"WebSocket connected for ticket_id: {self.ticket_id}")
        await self.accept()
        
        # Send chat history to the newly connected client
        await self.send_chat_history()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json.get('user_id')
        
        # Save message to database
        await self.save_message(user_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'first_name': text_data_json.get('first_name', ''),
                'last_name': text_data_json.get('last_name', ''),
                'user_type': text_data_json.get('user_type', ''),
                'timestamp': await self.get_timestamp()
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'first_name': event['first_name'],
            'last_name': event['last_name'],
            'user_type': event['user_type'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, user_id, message_content):
        try:
            user = User.objects.get(id=user_id)
            ticket = Ticket.objects.get(id=self.ticket_id)
            
            Message.objects.create(
                ticket=ticket,
                sender=user,
                content=message_content
            )
            return True
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            print(f"Error saving message: {str(e)}")
            return False

    @database_sync_to_async
    def get_timestamp(self):
        import datetime
        return datetime.datetime.now().isoformat()

    @database_sync_to_async
    def get_chat_history(self):
        try:
            messages = Message.objects.filter(ticket_id=self.ticket_id).order_by('timestamp')
            return [
                {
                    'message': msg.content,
                    'user_id': msg.sender.id,
                    'first_name': msg.sender.first_name,
                    'last_name': msg.sender.last_name,
                    'user_type': msg.sender.user_type,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            print(f"Error getting chat history: {str(e)}")
            return []

    async def send_chat_history(self):
        messages = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages
        }))
