from django.db import models

class KubeCluster(models.Model):
    """
    Cluster information
    """
    name = models.CharField(max_length=100, help_text="Cluster Name")
    api_server = models.GenericIPAddressField(help_text="Cluster API Server address, e.g 192.168.0.247")
    port = models.IntegerField(default=6443, help_text="API Server port, e.g 6443")
    description = models.TextField(blank=True, help_text="More")
    cluster_id = models.CharField(max_length=100, help_text="Cluster ID", blank=True)

    def __str__(self):
        return self.name