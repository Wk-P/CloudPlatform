from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class K8sAccount(models.Model):
    user = models.ForeignKey('ManagerCustomUser', on_delete=models.CASCADE, related_name='k8s_accounts')
    cluster_name = models.CharField(max_length=100)
    cluster_id = models.TextField(blank=True, null=True)
    kubeconfig = models.TextField()
    token = models.TextField(blank=True, null=True)
    token_expire_time = models.DateTimeField(blank=True, null=True)
    user_group = models.TextField(blank=True, null=True)
    namespace = models.CharField(max_length=100, default='default')
    k8s_api_server_url = models.CharField(max_length=100, blank=True, null=True)


class OtherAccount(models.Model):
    user = models.ForeignKey('ManagerCustomUser', on_delete=models.CASCADE, related_name='other_accounts')
    cluster_name = models.CharField(max_length=100)
    cluster_id = models.TextField(blank=True, null=True)


class ManagerCustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.uuid} - {self.username}"


