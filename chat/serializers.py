from rest_framework import serializers
from .models import Message, Attachment
from accounts.serializers import UserSerializer


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_name']


class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    upload_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Message
        fields = ['id', 'ticket', 'sender', 'content', 'timestamp', 'is_read', 'sender_details', 'attachments',
                  'upload_files']
        read_only_fields = ['sender', 'timestamp', 'is_read']

    def create(self, validated_data):
        upload_files = validated_data.pop('upload_files', [])

        # Set sender to current user
        validated_data['sender'] = self.context['request'].user

        # Create the message
        message = Message.objects.create(**validated_data)

        # Create attachments if any
        for file in upload_files:
            Attachment.objects.create(
                message=message,
                file=file,
                file_name=file.name
            )

        return message