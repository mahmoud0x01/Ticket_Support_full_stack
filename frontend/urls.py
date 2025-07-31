from django.urls import path
from .views import (
    home_view,
    login_view,
    signup_view,
    dashboard_view,
    ticket_detail_view,
    create_ticket_view,
    update_ticket_status  # Added this line to import the new view
)
from . import views
urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('tickets/new/', create_ticket_view, name='create_ticket'),
    path('logout/', views.logout_view, name='logout'),
    path('tickets/<int:ticket_id>/', ticket_detail_view, name='ticket_detail'),
    path('tickets/<int:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    path('tickets/<int:ticket_id>/update-status/', update_ticket_status, name='update_ticket_status'),  # Added this line for the new URL pattern
]