
from django.urls import path
from .views import ZohoDeskCreateTicketView

urlpatterns = [
    path('ticket/', ZohoDeskCreateTicketView.as_view(),
        name='ticket'),
]
