
from django.db import models



class TicketCase(models.Model):
    subject = models.CharField(max_length=255)
    description = models.TextField()
    department_id = models.CharField(max_length=20)
    contact_id = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='Abierto')
    ticket_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.subject} - {self.status}'

    
