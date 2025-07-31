from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer
from django.shortcuts import get_object_or_404


class IsOwnerOrSupport(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or support staff to view/edit it
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is owner or support staff
        return obj.created_by == request.user or request.user.user_type in ['support', 'admin']


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSupport]

    def get_queryset(self):
        user = self.request.user

        # If admin, show all tickets
        if user.user_type == 'admin':
            return Ticket.objects.all()
        
        # If support staff, show only assigned tickets
        if user.user_type == 'support':
            return Ticket.objects.filter(assigned_to=user)

        # For regular users, show only their tickets
        return Ticket.objects.filter(created_by=user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        ticket = self.get_object()
        status = request.data.get('status')

        if status not in [choice[0] for choice in Ticket.STATUS_CHOICES]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = status
        ticket.save()

        # Update support statistics if status changed to resolved
        if status == 'resolved' and ticket.assigned_to and hasattr(ticket.assigned_to, 'support_profile'):
            ticket.assigned_to.support_profile.tickets_resolved += 1
            ticket.assigned_to.support_profile.save()

        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        support_user_id = request.data.get('support_user_id')

        if support_user_id:
            try:
                support_user = User.objects.get(id=support_user_id, user_type='support')

                # Update old support staff statistics if any
                if ticket.assigned_to and hasattr(ticket.assigned_to, 'support_profile'):
                    ticket.assigned_to.support_profile.tickets_assigned -= 1
                    ticket.assigned_to.support_profile.save()

                # Update new support staff statistics
                ticket.assigned_to = support_user
                if hasattr(support_user, 'support_profile'):
                    support_user.support_profile.tickets_assigned += 1
                    support_user.support_profile.save()

                ticket.save()
                return Response(TicketSerializer(ticket).data)
            except User.DoesNotExist:
                return Response({'error': 'Support user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Unassign ticket
            if ticket.assigned_to and hasattr(ticket.assigned_to, 'support_profile'):
                ticket.assigned_to.support_profile.tickets_assigned -= 1
                ticket.assigned_to.support_profile.save()

            ticket.assigned_to = None
            ticket.save()
            return Response(TicketSerializer(ticket).data)
