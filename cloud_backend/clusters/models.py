from django.db import models

# Create your models here.
class K8sCluster(models.Model):
    name = models.CharField(max_length=100)
    api_server = models.URLField()
    token = models.TextField()
    kubeconfig_path = models.TextField()

class OpenStackCloud(models.Model):
    name = models.CharField(max_length=100)
    auth_url = models.URLField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)