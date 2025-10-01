from django.db import models

from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = (
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    managed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_users")
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Completion fields
    completion_report = models.TextField(blank=True)
    worked_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # def mark_completed(self, report: str, worked_hours):
    #     self.status = 'completed'
    #     self.completion_report = report
    #     self.worked_hours = worked_hours
    #     self.save()

    # def __str__(self):
    #     return f"{self.title} -> {self.assigned_to.username} [{self.status}]"
