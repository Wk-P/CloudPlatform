from django.test import TestCase, RequestFactory
from runtime_monitoring.models import KubeCluster
from state_manager.views import get_cluster_usage
from unittest.mock import patch, MagicMock
import json

class ClusterUsageTest(TestCase):
    def test_get_cluster_usage_real(self):
        cluster = KubeCluster.objects.create(
            name='k8s-cluster-minikube-cluster',
            api_server='192.168.0.247',
            port=8443,
            token='eyJhbGciOiJSUzI1NiIsImtpZCI6IlZfRzRrQUpOaU5iTHM1N1ZPQnk2ODlMYm8xbkZzOXRPRjlxMXRGZ2pvX1EifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzgyNDY2OTgxLCJpYXQiOjE3NTA5MzA5ODEsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiZjFmOTAyNzgtNTgxZS00ZTIwLThlNTktMjczODk2MmFjNTYwIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZWZhdWx0Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRqYW5nby1hZ2VudCIsInVpZCI6ImQ0N2ViNjRjLWI1ZmItNGI0Ny1iZjdiLWQwNzkyNjY2ZmQ0MiJ9fSwibmJmIjoxNzUwOTMwOTgxLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpkamFuZ28tYWdlbnQifQ.x-JIm17kazqAP6A8dW9KV8or2M-w487UuabiqKRgDG4z_C0EFKflJ9REiuIvPu7qUMAn9aK6ntkA7wvE2kIKvA0liZZiMX5O_65oAdUncfzQrsCfKUWHDzkvks4_Amk7E-4RVmOOKii3bdVzAVC03IJw-VExL7Qdv5w17ZXMYRgfneC3XJxAxrKrBhTxxD3kACxb66Iqg1vGUKNSf8pLMi0EV6cG7he5P4qIkKb3WMGCZnFzibPmyrWbtY282wZgoq2gSjXmVvRvBPxxRM8d7BAI3vd7aABi9UuO2A4vok4E2MPmpQKOzsw_BZOAgNfADzy4jmAfOjWbFLfThJCLdQ',
            description='Auto register...',
            cluster_id='9665489e-6fbb-4b7e-b00e-dc87aa3cbf36'
        )

        self.assertIsNotNone(cluster, "Need prepare the Object")

        factory = RequestFactory()
        request = factory.get("/fake-url")
        response = get_cluster_usage(request, cluster)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        print("test output:", data)
        self.assertIn("cpu_utilization", data)
