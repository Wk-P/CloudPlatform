from django.db import models

class KubeCluster(models.Model):
    """
    Cluster information
    """
    name = models.CharField(max_length=100, help_text="Cluster Name")
    api_server = models.GenericIPAddressField(help_text="Cluster API Server IP address (e.g., minikube IP from 'minikube ip')")
    port = models.IntegerField(default=8443, help_text="API Server port (8443 for minikube, 6443 for standard k8s)")
    description = models.TextField(blank=True, help_text="More")
    cluster_id = models.CharField(max_length=100, help_text="Cluster ID", blank=True)
    redis_report_endpoint = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Redis report service endpoint (cluster-specific), e.g http://<cluster-ip>:8099/report/read"
    )

    def __str__(self):
        return self.name