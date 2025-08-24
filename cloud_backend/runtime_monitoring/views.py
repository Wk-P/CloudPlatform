from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import KubeCluster
from .kube_client import get_core_client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from kubernetes import client
from django.utils import timezone
import json
import uuid
from django.conf import settings
from authentication.jwt_utils import jwt_required, jwt_decode

def get_clusters_base_info_list(request):
    results = list(KubeCluster.objects.all().values())

    return JsonResponse({"clusters": results})


def get_cluster_info(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    core = get_core_client(cluster.api_server, cluster.port, token)

    try:
        services = core.list_namespaced_service("kube-system")

        results = []
        for svc in services.items:
            results.append({
                "name": svc.metadata.name,
                "cluster_ip": svc.spec.cluster_ip,
                "ports": [
                    {
                        "port": p.port,
                        "target_port": p.target_port,
            "protocol": getattr(p, 'protocol', None)
                    } for p in svc.spec.ports or []
                ],
                "type": svc.spec.type,
        "url": f"https://{cluster.api_server}:{cluster.port}/api/v1/namespaces/kube-system/services/{svc.metadata.name}/proxy"
            })
        return JsonResponse({
            "api_server": f"https://{cluster.api_server}:{cluster.port}",
            "services": results
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def add_cluster_simple(request):
    try:
        # accept both JSON body and form-encoded payloads
        try:
            body = json.loads(request.body or b"{}")
        except Exception:
            # fallback to POST dict when content_type mismatches
            body = request.POST.dict() if hasattr(request, "POST") else {}

        api_server = body.get("api_server")
        # optional: verification is skipped; SA will be bound per-cluster separately
        # port may come as str; default to 8443
        try:
            port = int(body.get("port", 8443))
        except Exception:
            port = 8443
        name = body.get('name') or "auto"
        sa_token = (body.get('sa_token') or '').strip()
        namespace = (body.get('namespace') or 'default').strip() or 'default'

        # basic validation
        if not api_server:
            return JsonResponse({"error": "api_server is required"}, status=400)

        version_info = None

        # auto name generate
        name = f"k8s-cluster-{name}"

        cluster = KubeCluster.objects.create(
            name=name,
            api_server=api_server,
            port=port,
            description=f"Auto register {timezone.now()}",
            cluster_id=str(uuid.uuid4())
        )

        # Bind SA token to this cluster for current user (required)
        if not sa_token:
            return JsonResponse({"error": "sa_token is required to bind ServiceAccount for this cluster"}, status=400)
        # decode current user from JWT
        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        try:
            payload = jwt_decode(auth.split(' ', 1)[1])
            from authentication.models import ManagerCustomUser, K8sAccount
            user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
        except Exception:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        # create account binding
        try:
            from django.db import transaction
            with transaction.atomic():
                K8sAccount.objects.create(
                    user=user,
                    cluster=cluster,
                    cluster_name=cluster.name,
                    kubeconfig='',
                    token=sa_token,
                    token_expire_time=None,
                    user_group=None,
                    namespace=namespace or 'default',
                    k8s_api_server_url=f"https://{cluster.api_server}:{cluster.port}",
                )
        except Exception as ex:
            return JsonResponse({"error": f"Failed to bind SA token: {ex}"}, status=400)

        return JsonResponse({
            "message": "Cluster Add Success",
            "version": getattr(version_info, 'git_version', None) or getattr(version_info, 'gitVersion', None),
            "new_cluster": {
                "id": cluster.id,
                "name": cluster.name,
                "api_server": cluster.api_server,
                "port": cluster.port,
                "description": cluster.description,
                "cluster_id": cluster.cluster_id,
            }
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_nodes(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    v1 = get_core_client(cluster.api_server, cluster.port, token)

    try:
        nodes = v1.list_node()
        data = [{
            "name": node.metadata.name,
            "status": node.status.conditions[-1].type
        } for node in nodes.items]
        return JsonResponse({"nodes": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_pods(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    v1 = get_core_client(cluster.api_server, cluster.port, token)

    try:
        # filters
        ns = request.GET.get('namespace')
        label_selector = request.GET.get('labelSelector')
        limit = request.GET.get('limit')
        continue_token = request.GET.get('continue')

        list_kwargs = {}
        if label_selector:
            list_kwargs['label_selector'] = label_selector
        if limit:
            try:
                list_kwargs['limit'] = int(limit)
            except Exception:
                pass
        if continue_token:
            list_kwargs['_continue'] = continue_token

        # choose API based on namespace
        if ns:
            pods = v1.list_namespaced_pod(ns, **list_kwargs)
        else:
            pods = v1.list_pod_for_all_namespaces(**list_kwargs)     # V1PodList
        data = []

        # pod: V1Pod
        for pod in pods.items:
            data.append({
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "node": pod.spec.node_name,
                "restarts": sum([(c.restart_count or 0) for c in (pod.status.container_statuses or [])]),
                "created_at": pod.metadata.creation_timestamp.isoformat() if getattr(pod.metadata, 'creation_timestamp', None) else None
            })
        
        resp = {"pods": data}
        if hasattr(pods, 'metadata') and getattr(pods.metadata, '_continue', None):
            resp['continue'] = pods.metadata._continue
        return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 
    
def get_services(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    v1 = get_core_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        label_selector = request.GET.get('labelSelector')
        list_kwargs = {}
        if label_selector:
            list_kwargs['label_selector'] = label_selector

        services = v1.list_namespaced_service(ns, **list_kwargs) if ns else v1.list_service_for_all_namespaces(**list_kwargs)
        data = [{"name": s.metadata.name, "namespace": s.metadata.namespace} for s in services.items]
        return JsonResponse({"services": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_events(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    v1 = get_core_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        events = v1.list_namespaced_event(ns) if ns else v1.list_event_for_all_namespaces()
        data = [{"message": e.message, "type": e.type} for e in events.items]
        return JsonResponse({"events": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# apps, batch, autoscaling, etc
from .kube_client import get_apps_client, get_batch_client, get_autoscaling_client, get_networking_client, get_rbac_client, get_extensions_client


def get_jobs(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    batch = get_batch_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        jobs = batch.list_namespaced_job(ns) if ns else batch.list_job_for_all_namespaces()
        data = [{"name": j.metadata.name} for j in jobs.items]
        return JsonResponse({"jobs": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_deployments(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        label_selector = request.GET.get('labelSelector')
        list_kwargs = {}
        if label_selector:
            list_kwargs['label_selector'] = label_selector
        deployments = (
            apps_v1.list_namespaced_deployment(ns, **list_kwargs)
            if ns else apps_v1.list_deployment_for_all_namespaces(**list_kwargs)
        )
        data = [
            {
                "namespace": d.metadata.namespace,
                "name": d.metadata.name,
                "replicas": d.status.replicas,
                "ready": d.status.ready_replicas,
                "updated": d.status.updated_replicas
            }
            for d in deployments.items
        ]
        return JsonResponse({"deployments": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_daemonsets(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        daemonsets = (
            apps_v1.list_namespaced_daemon_set(ns)
            if ns else apps_v1.list_daemon_set_for_all_namespaces()
        )
        data = [
            {
                "namespace": d.metadata.namespace,
                "name": d.metadata.name,
                "number_ready": d.status.number_ready,
                "desired": d.status.desired_number_scheduled
            }
            for d in daemonsets.items
        ]
        return JsonResponse({"daemonsets": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def get_statefulsets(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        statefulsets = (
            apps_v1.list_namespaced_stateful_set(ns)
            if ns else apps_v1.list_stateful_set_for_all_namespaces()
        )
        data = [
            {
                "namespace": s.metadata.namespace,
                "name": s.metadata.name,
                "replicas": s.status.replicas,
                "ready": s.status.ready_replicas
            }
            for s in statefulsets.items
        ]
        return JsonResponse({"statefulsets": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_replicasets(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, token)
    try:
        ns = request.GET.get('namespace')
        replicasets = (
            apps_v1.list_namespaced_replica_set(ns)
            if ns else apps_v1.list_replica_set_for_all_namespaces()
        )
        data = [
            {
                "namespace": r.metadata.namespace,
                "name": r.metadata.name,
                "replicas": r.status.replicas,
                "ready": r.status.ready_replicas
            }
            for r in replicasets.items
        ]
        return JsonResponse({"replicasets": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_namespaces(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    token, err = _get_sa_token(request, cluster)
    if err:
        return err
    v1 = get_core_client(cluster.api_server, cluster.port, token)
    try:
        nss = v1.list_namespace()
        data = [{"name": ns.metadata.name, "status": getattr(ns.status, 'phase', None)} for ns in nss.items]
        return JsonResponse({"namespaces": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _get_sa_token(request, cluster):
    auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
    if not auth or not auth.startswith('Bearer '):
        return None, JsonResponse({'error': 'Unauthorized'}, status=401)
    token = auth.split(' ', 1)[1]
    try:
        payload = jwt_decode(token)
    except Exception as e:
        return None, JsonResponse({'error': f'Invalid token: {e}'}, status=401)
    try:
        from authentication.models import ManagerCustomUser
        user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
    except Exception:
        return None, JsonResponse({'error': 'User not found'}, status=404)
    # find K8sAccount bound to this cluster
    try:
        from authentication.models import K8sAccount
        acc = K8sAccount.objects.filter(user=user, cluster=cluster).order_by('-id').first()
    except Exception:
        acc = None
    if not acc or not acc.token:
        return None, JsonResponse({'error': 'No SA token bound for this cluster'}, status=400)
    return acc.token, None