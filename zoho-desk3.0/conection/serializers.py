
from rest_framework import serializers
from .models import TicketCase


class TicketCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCase
        fields = '__all__'
