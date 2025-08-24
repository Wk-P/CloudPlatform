from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .models import ManagerCustomUser
from .jwt_utils import jwt_encode, jwt_decode
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import base64
import json

# Create your views here.
class K8sLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request: Request):
        # Minimal issue-only JWT for experimental usage
        # Accept either username or anonymous client id
        username = request.data.get('username') or 'anonymous'
        user, _ = ManagerCustomUser.objects.get_or_create(username=username, defaults={'password': '!'})
        token = jwt_encode({'sub': str(user.uuid), 'username': user.username})
        return Response({'token': token})


class RegisterView(APIView):
    """Simple username/password registration and immediate JWT issue."""
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request: Request):
        username = (request.data.get('username') or '').strip()
        password = (request.data.get('password') or '').strip()
        if not username or not password:
            return Response({'detail': 'username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if ManagerCustomUser.objects.filter(username=username).exists():
            return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = ManagerCustomUser(username=username)
            user.set_password(password)
            user.save()
        except IntegrityError:
            return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        token = jwt_encode({'sub': str(user.uuid), 'username': user.username})
        return Response({'token': token, 'user': {'uuid': str(user.uuid), 'username': user.username}}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Username/password login to obtain JWT."""
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request: Request):
        username = (request.data.get('username') or '').strip()
        password = (request.data.get('password') or '').strip()
        if not username or not password:
            return Response({'detail': 'username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'detail': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token = jwt_encode({'sub': str(user.uuid), 'username': user.username})
        return Response({'token': token, 'user': {'uuid': str(user.uuid), 'username': user.username}})


class MeView(APIView):
    """Return current user info from JWT Bearer."""
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request: Request):
        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Bearer '):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth.split(' ', 1)[1]
        try:
            payload = jwt_decode(token)
        except Exception as e:
            return Response({'detail': f'Invalid token: {e}'}, status=status.HTTP_401_UNAUTHORIZED)
        user = None
        try:
            user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
        except ManagerCustomUser.DoesNotExist:
            pass
        return Response({'user': {'uuid': payload.get('sub'), 'username': (user.username if user else payload.get('username'))}})


class UpdateSATokenView(APIView):
    """Deprecated: SA token is now bound per-cluster via K8sAccount. Keep for compatibility returning 410."""
    def post(self, request: Request):
        return Response({'detail': 'deprecated: bind SA token when registering cluster'}, status=status.HTTP_410_GONE)


class K8sAccountView(APIView):
    """Create or update a simple K8sAccount for current user to store SA token.
    Requires Bearer token in Authorization header.
    Body: { token: string, cluster_name?: string, namespace?: string, k8s_api_server_url?: string }
    """
    def post(self, request: Request):
        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Bearer '):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            payload = jwt_decode(auth.split(' ', 1)[1])
        except Exception as e:
            return Response({'detail': f'Invalid token: {e}'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
        except ManagerCustomUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = (request.data.get('token') or '').strip()
        if not token:
            return Response({'detail': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)
        cluster_name = (request.data.get('cluster_name') or 'default').strip()
        namespace = (request.data.get('namespace') or 'default').strip()
        k8s_api_server_url = (request.data.get('k8s_api_server_url') or '').strip() or None

        # Lazy import to avoid circulars
        from .models import K8sAccount

        acc = K8sAccount.objects.create(
            user=user,
            cluster_name=cluster_name,
            kubeconfig='',
            token=token,
            token_expire_time=None,
            user_group=None,
            namespace=namespace,
            k8s_api_server_url=k8s_api_server_url,
        )
        return Response({'ok': True, 'account_id': acc.id, 'cluster_name': acc.cluster_name})


class BindK8sAccountToClusterView(APIView):
    """Bind or update a K8sAccount (SA token) for the current user to a specific cluster.
    Body: { cluster_id: int, token: string, namespace?: string }
    Returns: { ok: true, cluster_id, account_id }
    """
    def post(self, request: Request):
        # Auth: Bearer JWT
        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Bearer '):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            payload = jwt_decode(auth.split(' ', 1)[1])
        except Exception as e:
            return Response({'detail': f'Invalid token: {e}'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
        except ManagerCustomUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Params
        data = request.data or {}
        cluster_id = data.get('cluster_id')
        token = (data.get('token') or '').strip()
        namespace = (data.get('namespace') or 'default').strip() or 'default'
        if not cluster_id:
            return Response({'detail': 'cluster_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not token:
            return Response({'detail': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve cluster
        try:
            from runtime_monitoring.models import KubeCluster
            cluster = KubeCluster.objects.get(id=cluster_id)
        except Exception:
            return Response({'detail': 'Cluster not found'}, status=status.HTTP_404_NOT_FOUND)

        # Upsert K8sAccount
        from .models import K8sAccount
        from django.db import transaction
        with transaction.atomic():
            acc = K8sAccount.objects.filter(user=user, cluster=cluster).order_by('-id').first()
            if acc is None:
                acc = K8sAccount.objects.create(
                    user=user,
                    cluster=cluster,
                    cluster_name=cluster.name,
                    kubeconfig='',
                    token=token,
                    token_expire_time=None,
                    user_group=None,
                    namespace=namespace,
                    k8s_api_server_url=f"https://{cluster.api_server}:{cluster.port}",
                )
            else:
                acc.token = token
                acc.namespace = namespace
                acc.k8s_api_server_url = f"https://{cluster.api_server}:{cluster.port}"
                acc.save(update_fields=['token', 'namespace', 'k8s_api_server_url'])

        return Response({'ok': True, 'cluster_id': cluster.id, 'account_id': acc.id})


def _b64url_decode_nopad(data_str: str) -> bytes:
    padding = '=' * (-len(data_str) % 4)
    return base64.urlsafe_b64decode(data_str + padding)


def _parse_sa_jwt_noverify(token: str) -> dict:
    try:
        _h, p, _s = token.split('.')
        return json.loads(_b64url_decode_nopad(p))
    except Exception:
        return {}


def _k8s_api_client_from_token(host: str, token: str):
    try:
        from kubernetes import client
    except Exception as e:
        raise RuntimeError(f'kubernetes client not available: {e}')
    cfg = client.Configuration()
    cfg.host = host
    cfg.verify_ssl = bool(settings.K8S_TLS.get('VERIFY_SSL', False))
    if settings.K8S_TLS.get('CA_CERT'):
        cfg.ssl_ca_cert = settings.K8S_TLS['CA_CERT']
    cfg.debug = False
    cfg.api_key = { 'authorization': f'Bearer {token}' }
    return client.ApiClient(cfg)


class SAInfoView(APIView):
    """Return ServiceAccount info and self rules using the provided SA token.
    Body: { token: str, k8s_api_server_url: str, namespace?: str }
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request):
        token = (request.data.get('token') or '').strip()
        host = (request.data.get('k8s_api_server_url') or '').strip()
        ns = (request.data.get('namespace') or '').strip() or None
        if not token:
            return Response({'detail': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not host:
            return Response({'detail': 'k8s_api_server_url is required'}, status=status.HTTP_400_BAD_REQUEST)

        claims = _parse_sa_jwt_noverify(token)
        sa_name = claims.get('kubernetes.io/serviceaccount/service-account.name') or None
        sa_ns = claims.get('kubernetes.io/serviceaccount/namespace') or None
        issuer = claims.get('iss') or None
        subject = claims.get('sub') or None

        # prefer provided namespace else claim namespace else default
        use_ns = ns or sa_ns or 'default'

        try:
            from kubernetes import client
            api_client = _k8s_api_client_from_token(host, token)
            auth_api = client.AuthorizationV1Api(api_client)
            body = client.V1SelfSubjectRulesReview(spec=client.V1SelfSubjectRulesReviewSpec(namespace=use_ns))
            ssrr = auth_api.create_self_subject_rules_review(body=body)
            rules = client.ApiClient().sanitize_for_serialization(ssrr)
        except Exception as e:
            return Response({'detail': f'Failed to query rules: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        resp = {
            'service_account': {
                'name': sa_name,
                'namespace': sa_ns,
                'issuer': issuer,
                'subject': subject,
            },
            'cluster': {
                'api_server_url': host,
                'verify_ssl': bool(settings.K8S_TLS.get('VERIFY_SSL', False)),
            },
            'query_namespace': use_ns,
            'rules': rules,
        }
        return Response(resp)