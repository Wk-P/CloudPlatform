from django.test import TestCase, Client
from unittest.mock import patch
from types import SimpleNamespace
from authentication.models import ManagerCustomUser, K8sAccount
from authentication.jwt_utils import jwt_encode
from .models import KubeCluster


class RuntimeMonitoringTests(TestCase):
    def setUp(self):
        self.client = Client()
        # platform user + JWT
        self.user = ManagerCustomUser.objects.create_user(username='u1', password='p')
        self.jwt = jwt_encode({'sub': str(self.user.uuid), 'username': self.user.username})
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {self.jwt}"}
        # cluster + SA binding
        self.cluster = KubeCluster.objects.create(name="c1", api_server="1.2.3.4", port=6443, description="", cluster_id="cid-1")
        K8sAccount.objects.create(user=self.user, cluster=self.cluster, cluster_name=self.cluster.name, kubeconfig='', token='sa-token', namespace='default', k8s_api_server_url='https://1.2.3.4:6443')

    @patch('runtime_monitoring.views.get_core_client')
    def test_get_nodes_pods_services(self, mock_core):
        # stub client
        def _dt():
            import datetime
            return datetime.datetime.utcnow()
        node = SimpleNamespace(metadata=SimpleNamespace(name='n1'), status=SimpleNamespace(conditions=[SimpleNamespace(type='Ready')]))
        pod = SimpleNamespace(
            metadata=SimpleNamespace(namespace='default', name='p1', creation_timestamp=_dt()),
            status=SimpleNamespace(phase='Running', container_statuses=[SimpleNamespace(restart_count=0)]),
            spec=SimpleNamespace(node_name='n1')
        )
        svc = SimpleNamespace(
            metadata=SimpleNamespace(namespace='default', name='s1'),
            spec=SimpleNamespace(type='ClusterIP', cluster_ip='10.0.0.1', ports=[SimpleNamespace(port=80, target_port=8080, protocol='TCP')])
        )
        class Stub:
            def list_node(self):
                return SimpleNamespace(items=[node])
            def list_pod_for_all_namespaces(self, **kwargs):
                return SimpleNamespace(items=[pod])
            def list_service_for_all_namespaces(self):
                return SimpleNamespace(items=[svc])
        mock_core.return_value = Stub()

        # nodes
        r = self.client.get(f"/api/runtime/clusters/{self.cluster.id}/nodes/", **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('nodes', r.json())
        # pods
        r = self.client.get(f"/api/runtime/clusters/{self.cluster.id}/pods/", **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('pods', r.json())
        # services
        r = self.client.get(f"/api/runtime/clusters/{self.cluster.id}/services/", **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('services', r.json())

    def test_add_cluster_requires_sa_and_auth(self):
        # missing auth
        r = self.client.post('/api/runtime/clusters/add/', data={'api_server':'1.1.1.1','port':8443,'name':'x'}, content_type='application/json')
        self.assertEqual(r.status_code, 400)
        # with auth but missing sa_token
        r = self.client.post('/api/runtime/clusters/add/', data={'api_server':'1.1.1.1','port':8443,'name':'x'}, content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 400)
        # full params
        r = self.client.post('/api/runtime/clusters/add/', data={'api_server':'1.1.1.2','port':8443,'name':'x','sa_token':'t','namespace':'default'}, content_type='application/json', **self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertIn('new_cluster', r.json())
