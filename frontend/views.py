from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from tickets.models import Ticket
from accounts.models import User
from accounts.serializers import UserSerializer
from tickets.serializers import TicketSerializer

from django.contrib.auth import logout
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from datetime import datetime

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid email or password"

    return render(request, 'frontend/login.html', {'error': error})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        age = request.POST.get('age')
        user_type = request.POST.get('user_type', 'user')

        if password != confirm_password:
            error = "Passwords don't match"
        elif User.objects.filter(email=email).exists():
            error = "Email already registered"
        else:
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                age=age,
                user_type=user_type
            )

            # Log user in
            login(request, user)
            return redirect('dashboard')

    return render(request, 'frontend/signup.html', {'error': error})


@login_required
def dashboard_view(request):
    user = request.user
    print(f"Dashboard view - User: {user}, User type: {getattr(user, 'user_type', 'unknown')}")

    # Check if user is authenticated
    if not user.is_authenticated:
        print("User is not authenticated")
        return redirect('login')  # Redirect to your login URL

    # Debug: Check all tickets in the database
    all_tickets = Ticket.objects.all()
    print(f"Total tickets in database: {all_tickets.count()}")
    for ticket in all_tickets:
        print(f"Ticket ID: {ticket.id}, Created by: {ticket.created_by}, Status: {ticket.status}")

    if hasattr(user, 'user_type') and user.user_type in ['support', 'admin']:
        # For support staff and admins, show all tickets
        tickets = Ticket.objects.all().order_by('-created_at')
        print(f"Support/Admin user - Showing all tickets: {tickets.count()}")

        # Additional filtering options for support
        status_filter = request.GET.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter)
            print(f"Filtered by status '{status_filter}': {tickets.count()} tickets")

        # Filter for assigned tickets
        assigned_filter = request.GET.get('assigned')
        if assigned_filter == 'me':
            tickets = tickets.filter(assigned_to=user)
            print(f"Filtered by assigned to me: {tickets.count()} tickets")
        elif assigned_filter == 'unassigned':
            tickets = tickets.filter(assigned_to__isnull=True)
            print(f"Filtered by unassigned: {tickets.count()} tickets")
    else:
        # For regular users, show only their tickets
        tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')
        print(f"Regular user - Showing user's tickets: {tickets.count()}")

        # Status filtering for users
        status_filter = request.GET.get('status')
        if status_filter:
            tickets = tickets.filter(status=status_filter)
            print(f"Filtered by status '{status_filter}': {tickets.count()} tickets")

    context = {
        'tickets': tickets,
        'user': user,
        'status_filter': status_filter if 'status_filter' in locals() else '',
        'assigned_filter': assigned_filter if 'assigned_filter' in locals() else ''
    }

    return render(request, 'frontend/dashboard.html', context)


@login_required
def create_ticket_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'medium')

        # Create ticket
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            created_by=request.user,
            status='open'
        )

        # Update user statistics
        if hasattr(request.user, 'profile'):
            request.user.profile.tickets_submitted += 1
            request.user.profile.save()

        return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'frontend/create_ticket.html')


@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check if user has permission to view this ticket
    if request.user.user_type == 'admin':
        # Admin can view all tickets
        pass
    elif request.user.user_type == 'support':
        # Support staff can only view tickets assigned to them
        if request.user != ticket.assigned_to:
            return redirect('dashboard')
    elif request.user == ticket.created_by:
        # Regular users can view their own tickets
        pass
    else:
        # No permission
        return redirect('dashboard')

    # Get support staff for assignment
    support_staff = User.objects.filter(user_type='support')

    context = {
        'ticket': ticket,
        'support_staff': support_staff,
        'user': request.user
    }

    return render(request, 'frontend/ticket_detail.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')  # or wherever you want to redirect after logout

@login_required
def assign_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check if user has permission to assign this ticket
        if request.user.user_type != 'admin':
            return redirect('dashboard')
        
        # Handle different assignment options
        support_id = request.POST.get('support_id')
        assigned_to = request.POST.get('assigned_to')
        
        if support_id == 'self':
            # Assign to the current user
            ticket.assigned_to = request.user
        elif support_id == 'unassign':
            # Unassign the ticket
            ticket.assigned_to = None
        elif support_id:
            # Assign to a specific support staff
            try:
                support_user = User.objects.get(id=support_id)
                if support_user.user_type == 'support':
                    ticket.assigned_to = support_user
            except User.DoesNotExist:
                pass
        elif assigned_to:
            # Alternative way to assign using assigned_to field
            try:
                if assigned_to == '':
                    ticket.assigned_to = None
                else:
                    support_user = User.objects.get(id=assigned_to)
                    ticket.assigned_to = support_user
            except User.DoesNotExist:
                pass
        
        ticket.save()
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    return redirect('ticket_detail', ticket_id=ticket_id)

@login_required
def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check if user has permission to update this ticket
        if request.user.user_type not in ['support', 'admin'] and request.user != ticket.assigned_to:
            return redirect('dashboard')
        
        new_status = request.POST.get('status')
        old_status = ticket.status
        
        if new_status in [choice[0] for choice in Ticket.STATUS_CHOICES]:
            # Get display values for statuses
            old_status_display = dict(Ticket.STATUS_CHOICES).get(old_status, old_status)
            
            ticket.status = new_status
            ticket.save()
            
            new_status_display = dict(Ticket.STATUS_CHOICES).get(new_status, new_status)
            
            # Update support statistics if status changed to resolved
            if new_status == 'resolved' and ticket.assigned_to and hasattr(ticket.assigned_to, 'support_profile'):
                ticket.assigned_to.support_profile.tickets_resolved += 1
                ticket.assigned_to.support_profile.save()
            
            # Send system message to chat about status update
            if old_status != new_status:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'chat_{ticket_id}',
                    {
                        'type': 'chat_message',
                        'message': f"Ticket status updated from '{old_status_display}' to '{new_status_display}'",
                        'user_id': 0,  # System message
                        'first_name': 'System',
                        'last_name': '',
                        'user_type': 'system',
                        'timestamp': datetime.now().isoformat()
                    }
                )
        
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    return redirect('ticket_detail', ticket_id=ticket_id)