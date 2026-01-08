from django.test import TestCase, Client
from unittest.mock import patch
from types import SimpleNamespace
from runtime_monitoring.models import KubeCluster
from authentication.models import ManagerCustomUser, K8sAccount
from authentication.jwt_utils import jwt_encode
import json



class StateManagerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = ManagerCustomUser.objects.create_user(username='u2', password='p')
        self.jwt = jwt_encode({'sub': str(self.user.uuid)})
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.jwt}"}
        
        # Read from environment or use localhost for testing
        import os
        test_api = os.getenv('TEST_K8S_API_SERVER', '127.0.0.1')
        test_port = int(os.getenv('TEST_K8S_API_PORT', '8443'))
        
        self.cluster = KubeCluster.objects.create(
            name="test-cluster",
            api_server=test_api,
            port=test_port,
            description="test",
            cluster_id="test-id"
        )
        K8sAccount.objects.create(
            user=self.user,
            cluster=self.cluster,
            cluster_name=self.cluster.name,
            kubeconfig='',
            token='sa-token',  # 可手动指定测试 token
            namespace='default',
            k8s_api_server_url=f'https://{self.cluster.api_server}:{self.cluster.port}'
        )

    @patch('state_manager.views.client.CoreV1Api')
    @patch('state_manager.views.client.CustomObjectsApi')
    def test_get_cluster_usage_success(self, mock_metrics, mock_core):
        """Test cluster usage API returns expected fields when metrics are available."""
        node = SimpleNamespace(
            status=SimpleNamespace(capacity={'cpu': '2', 'memory': '2048000Ki'}),
            metadata=SimpleNamespace()
        )
        mock_core.return_value.list_node.return_value = SimpleNamespace(items=[node])
        mock_metrics.return_value.list_cluster_custom_object.return_value = {
            'items': [
                {'usage': {'cpu': '2000m', 'memory': '1024000Ki'}},
            ]
        }
        r = self.client.get(f'/api/state/resources/cluster/{self.cluster.id}/', **self.auth)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for key in [
            'total_cpu', 'used_cpu', 'cpu_utilization',
            'total_memory', 'used_memory', 'memory_utilization'
        ]:
            self.assertIn(key, data)

    @patch('state_manager.views.client.CoreV1Api')
    @patch('state_manager.views.client.AppsV1Api')
    @patch('state_manager.views.DynamicClient')
    @patch('state_manager.views.ApiClient')
    def test_run_get_and_scale(self, mock_api_client, mock_dyn, mock_apps, mock_core):
        """Test run_command API for get pods and scale deployment."""
        pod = SimpleNamespace(
            metadata=SimpleNamespace(namespace='default', name='p1', creation_timestamp=None),
            status=SimpleNamespace(phase='Running', container_statuses=[SimpleNamespace(restart_count=0)]),
            spec=SimpleNamespace(node_name='n1')
        )
        mock_core.return_value.list_pod_for_all_namespaces.return_value = SimpleNamespace(items=[pod])
        r = self.client.post('/api/state/run/cmd/', data=json.dumps({
            'action': 'get', 'resource': 'pods', 'cluster_id': self.cluster.id
        }), content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('stdout', r.json())
        r = self.client.post('/api/state/run/cmd/', data=json.dumps({
            'action': 'scale', 'resource': 'deployments', 'name': 'd1', 'replicas': 2, 'cluster_id': self.cluster.id, 'namespace': 'default'
        }), content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('stdout', r.json())

    def test_cluster_usage_requires_binding(self):
        """Test cluster usage API returns 400 if no SA token bound."""
        c = KubeCluster.objects.create(
            name="c3",
            api_server="1.1.1.1",
            port=6443,
            description="",
            cluster_id="cid-3"
        )
        r = self.client.get(f'/api/state/resources/cluster/{c.id}/', **self.auth)
        self.assertEqual(r.status_code, 400)
