import requests
from django.test import TestCase, Client
import json
from pathlib import Path

class AuthEndpointsTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_register_and_login(self):
		r = self.client.post('/api/auth/register/', data=json.dumps({'username':'t1','password':'p1'}), content_type='application/json')
		self.assertIn(r.status_code, [200, 201, 400])  # allow created or repeated runs
		r = self.client.post('/api/auth/login/', data=json.dumps({'username':'t1','password':'p1'}), content_type='application/json')
		self.assertEqual(r.status_code, 200)
		self.assertIn('token', r.json())


class K8sApiServerTests(TestCase):
    def setUp(self):
        # real token file
        self.token = json.loads((Path(__file__).parent / 'k8s_test_auth_token' / 'token.json').read_text())[0]['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
        self.api_server = 'https://192.168.0.247:8443'

    def test_k8s_version(self):
        
        r = requests.get(f'{self.api_server}/version', headers=self.headers, verify=False, timeout=5)
        self.assertEqual(r.status_code, 200)
        self.assertIn('gitVersion', r.json())
