from rest_framework import serializers
from .models import Ticket
from accounts.serializers import UserSerializer
from accounts.models import User, UserProfile, SupportProfile


class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='support'), required=False,
                                                     allow_null=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'created_by', 'assigned_to',
                  'status', 'priority', 'created_by_details', 'assigned_to_details']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        ticket = Ticket.objects.create(created_by=user, **validated_data)

        # Update user profile statistics
        if hasattr(user, 'profile'):
            user.profile.tickets_submitted += 1
            user.profile.save()

        return ticket

    def update(self, instance, validated_data):
        old_status = instance.status
        old_assigned_to = instance.assigned_to

        # Update the ticket
        instance = super().update(instance, validated_data)

        # Update support staff statistics if assignment or status changed
        if 'assigned_to' in validated_data and validated_data['assigned_to'] != old_assigned_to:
            # If previously assigned to someone, decrease their count
            if old_assigned_to and hasattr(old_assigned_to, 'support_profile'):
                old_assigned_to.support_profile.tickets_assigned -= 1
                old_assigned_to.support_profile.save()

            # If newly assigned to someone, increase their count
            if instance.assigned_to and hasattr(instance.assigned_to, 'support_profile'):
                instance.assigned_to.support_profile.tickets_assigned += 1
                instance.assigned_to.support_profile.save()

        # Update resolved tickets count if status changed to resolved
        if 'status' in validated_data and validated_data['status'] == 'resolved' and old_status != 'resolved':
            if instance.assigned_to and hasattr(instance.assigned_to, 'support_profile'):
                instance.assigned_to.support_profile.tickets_resolved += 1
                instance.assigned_to.support_profile.save()

        return instance