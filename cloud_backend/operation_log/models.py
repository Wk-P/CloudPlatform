from django.db import models

# Create your models here.

class OperationLog(models.Model):
    user = models.CharField(max_length=50)
    operation = models.TextField()
    result = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
