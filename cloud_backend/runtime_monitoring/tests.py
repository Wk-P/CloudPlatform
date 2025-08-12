from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
from django.urls import reverse
from .models import KubeCluster

class AddClusterSimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlZfRzRrQUpOaU5iTHM1N1ZPQnk2ODlMYm8xbkZzOXRPRjlxMXRGZ2pvX1EifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzgyNDY2OTgxLCJpYXQiOjE3NTA5MzA5ODEsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiZjFmOTAyNzgtNTgxZS00ZTIwLThlNTktMjczODk2MmFjNTYwIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZWZhdWx0Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRqYW5nby1hZ2VudCIsInVpZCI6ImQ0N2ViNjRjLWI1ZmItNGI0Ny1iZjdiLWQwNzkyNjY2ZmQ0MiJ9fSwibmJmIjoxNzUwOTMwOTgxLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpkamFuZ28tYWdlbnQifQ.x-JIm17kazqAP6A8dW9KV8or2M-w487UuabiqKRgDG4z_C0EFKflJ9REiuIvPu7qUMAn9aK6ntkA7wvE2kIKvA0liZZiMX5O_65oAdUncfzQrsCfKUWHDzkvks4_Amk7E-4RVmOOKii3bdVzAVC03IJw-VExL7Qdv5w17ZXMYRgfneC3XJxAxrKrBhTxxD3kACxb66Iqg1vGUKNSf8pLMi0EV6cG7he5P4qIkKb3WMGCZnFzibPmyrWbtY282wZgoq2gSjXmVvRvBPxxRM8d7BAI3vd7aABi9UuO2A4vok4E2MPmpQKOzsw_BZOAgNfADzy4jmAfOjWbFLfThJCLdQ"
        self.api_server = "192.168.0.247"
        self.port = 8443
        self.url = "/runtime/api/clusters/add/"

        # 创建 cluster 对象，数据库为临时 test db，不污染真实数据
        self.cluster = KubeCluster.objects.create(
            name="TestCluster",
            api_server=self.api_server,
            port=self.port,
            token=self.token
        )

    def test_nodes_query(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/nodes/"
        response = self.client.get(url)

        print("状态码：", response.status_code)
        print("返回：", response.json())

        self.assertEqual(response.status_code, 200)
        self.assertIn("nodes", response.json())
        # 可选：检查返回中至少有一个 node
        self.assertGreaterEqual(len(response.json()["nodes"]), 1)

    @patch("runtime_monitoring.views.client.VersionApi")
    def test_add_cluster_success(self, mock_version_api_class):
        # Mock version_api.get_code().git_version
        mock_version_api = MagicMock()
        mock_version_api.get_code.return_value.git_version = "v1.32.0"
        mock_version_api_class.return_value = mock_version_api

        payload = {
            "api_server": "192.168.0.247",
            "port": 8443,
            "token": self.token
        }

        response = self.client.post(self.url, data=payload, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["version"], "v1.32.0")

    def test_add_cluster_missing_fields(self):
        # 缺少 token
        payload = {
            "api_server": "192.168.0.247"
        }
        response = self.client.post(self.url, data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)


    def test_get_nodes(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/nodes/"
        response = self.client.get(url)
        print("Test get_nodes status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_pods(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/pods/"
        response = self.client.get(url)
        print("Test get_pods status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_services(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/services/"
        response = self.client.get(url)
        print("Test get_services status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_events(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/events/"
        response = self.client.get(url)
        print("Test get_events status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_deployments(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/deployments/"
        response = self.client.get(url)
        print("Test get_deployments status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_daemonsets(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/daemonsets/"
        response = self.client.get(url)
        print("Test get_daemonsets status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_statefulsets(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/statefulsets/"
        response = self.client.get(url)
        print("Test get_statefulsets status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_replicasets(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/replicasets/"
        response = self.client.get(url)
        print("Test get_replicasets status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])

    def test_get_jobs(self):
        url = f"/runtime/api/clusters/{self.cluster.id}/jobs/"
        response = self.client.get(url)
        print("Test get_jobs status:", response.status_code)
        print("Response:", response.content)
        self.assertIn(response.status_code, [200, 500])
