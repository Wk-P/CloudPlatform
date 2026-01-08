from django.test import TestCase, Client
from .models import IngressBlacklistItem, IngressTrafficSample
import datetime
import os
import json


class IngressEndpointsTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_get_blacklist_empty_then_with_data(self):
		# initial empty
		r = self.client.get('/api/ingress/blacklist/')
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertIn('items', data)
		self.assertIsInstance(data['items'], list)
		self.assertEqual(len(data['items']), 0)

		# create one entry
		IngressBlacklistItem.objects.create(
			source='1.2.3.4', action='block', scope='global', reason='test'
		)
		r = self.client.get('/api/ingress/blacklist/')
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertGreaterEqual(len(data.get('items', [])), 1)
		first = data['items'][0]
		self.assertIn('updated_at', first)

	def test_get_traffic_trend_empty_then_with_data(self):
		# empty
		r = self.client.get('/api/ingress/traffic/trend/?limit=5')
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertIn('points', data)
		self.assertIsInstance(data['points'], list)
		self.assertEqual(len(data['points']), 0)

		# insert some samples
		now = datetime.datetime.now(datetime.timezone.utc)
		for i in range(3):
			IngressTrafficSample.objects.create(ts=now + datetime.timedelta(seconds=i), value=float(i))
		r = self.client.get('/api/ingress/traffic/trend/?limit=5')
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertGreaterEqual(len(data.get('points', [])), 3)
		# ascending order by time
		pts = data['points']
		self.assertLessEqual(pts[0]['ts'], pts[-1]['ts'])

import requests

class LiveSAInfoTests(TestCase):
	"""Live integration test to query SA info via ingress-proxied K8s API.

	Token sources (in order):
	1) File cloud_backend/authentication/k8s_test_auth_token/token.json
	   - Supports array format: [{"token": "..."}, ...] or object format {"token": "..."}
	2) Env TEST_SA_TOKEN or K8S_SA_TOKEN

	Host source:
	- Env TEST_K8S_API_SERVER_URL (required for anomaly detection service endpoint)
	- No hardcoded defaults - test will skip if not configured

	Test is skipped if token missing or 'kubernetes' package unavailable.
	"""

	def setUp(self):
		from runtime_monitoring.models import KubeCluster
		self.client = Client()
		# Anomaly detection service endpoint - must be configured via env or cluster.redis_report_endpoint
		self.host = os.getenv('TEST_K8S_API_SERVER_URL')
		if not self.host:
			cluster = KubeCluster.objects.first()
			if cluster and cluster.redis_report_endpoint:
				self.host = cluster.redis_report_endpoint.replace('/report/read', '')
			else:
				self.skipTest('TEST_K8S_API_SERVER_URL not set and no cluster.redis_report_endpoint configured')

    # test nginx backend service
	def test_sa_info_via_ingress_http(self):
		r = requests.get(self.host)
		self.assertEqual(r.status_code, 200)
		print(r.content.decode('utf-8'))
		
    
    # test nginx ingress-controller
	def test_sa_info_via_ingress_controller(self):
		r = requests.get(f'{self.host}/api/auth/k8s/sa-info/')
		self.assertEqual(r.status_code, 200)
		print(r.content.decode('utf-8'))