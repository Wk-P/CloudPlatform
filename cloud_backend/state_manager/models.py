from django.db import models
from django.contrib.auth import get_user_model

class CommandRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    cluster_id = models.CharField(max_length=64)
    command = models.TextField()
    stdout = models.TextField(blank=True, null=True)
    stderr = models.TextField(blank=True, null=True)
    returncode = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)