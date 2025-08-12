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

def get_clusters_base_info_list(request):
    results = list(KubeCluster.objects.all().values())

    return JsonResponse({"clusters": results})


def get_cluster_info(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    core = get_core_client(cluster.api_server, cluster.port, cluster.token)

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
                        "protocol": p.protocal
                    } for p in svc.spec.ports or []
                ],
                "type": svc.spec.type,
                "url": f"https://{cluster.api_server}:{cluster.port}/api/v1/namespaces/kube-system/services/{svc.metadata}/proxy"
            })
        return JsonResponse({
            "api_server": f"https://{cluster.api_server}:{cluster.port}",
            "services": results
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_cluster_simple(request):
    try:
        body = json.loads(request.body)
        api_server = body.get("api_server")
        port = int(body.get("port", 8443))
        token = body.get("token")
        name = body.get('name')

        # verify connection
        configuration = client.Configuration()
        configuration.host = f"https://{api_server}:{port}"
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)

        version_api = client.VersionApi()
        version_info = version_api.get_code()

        # auto name generate
        name = f"k8s-cluster-{name}"

        cluster = KubeCluster.objects.create(
            name=name,
            api_server=api_server,
            port=port,
            token=token,
            description=f"Auto register {timezone.now()}",
            cluster_id=str(uuid.uuid4())
        )

        return JsonResponse({
            "message": "Cluster Add Success",
            "new_cluster": cluster
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_nodes(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    v1 = get_core_client(cluster.api_server, cluster.port, cluster.token)

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
    v1 = get_core_client(cluster.api_server, cluster.port, cluster.token)

    try:
        pods = v1.list_pod_for_all_namespaces()     # V1PodList
        data = []

        # pod: V1Pod
        for pod in pods.items:
             data.append({
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "node": pod.spec.node_name,
                "restarts": sum([c.restart_count for c in pod.status.container_statuses or []]),
                "created_at": pod.metadata.creation_timestamp.isoformat()
            })
             
        return JsonResponse({"pods": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 
    
def get_services(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    v1 = get_core_client(cluster.api_server, cluster.port, cluster.token)
    try:
        services = v1.list_service_for_all_namespaces()
        data = [{"name": s.metadata.name, "namespace": s.metadata.namespace} for s in services.items]
        return JsonResponse({"services": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_events(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    v1 = get_core_client(cluster.api_server, cluster.port, cluster.token)
    try:
        events = v1.list_event_for_all_namespaces()
        data = [{"message": e.message, "type": e.type} for e in events.items]
        return JsonResponse({"events": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# apps, batch, autoscaling, etc
from .kube_client import get_apps_client, get_batch_client, get_autoscaling_client, get_networking_client, get_rbac_client, get_extensions_client

def get_deployments(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    apps = get_apps_client(cluster.api_server, cluster.port, cluster.token)
    try:
        deployments = apps.list_deployment_for_all_namespaces()
        data = [{"name": d.metadata.name, "namespace": d.metadata.namespace} for d in deployments.items]
        return JsonResponse({"deployments": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_jobs(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    batch = get_batch_client(cluster.api_server, cluster.port, cluster.token)
    try:
        jobs = batch.list_job_for_all_namespaces()
        data = [{"name": j.metadata.name} for j in jobs.items]
        return JsonResponse({"jobs": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_deployments(request, id):
    cluster = get_object_or_404(KubeCluster, id=id)
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, cluster.token)
    try:
        deployments = apps_v1.list_deployment_for_all_namespaces()
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
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, cluster.token)
    try:
        daemonsets = apps_v1.list_daemon_set_for_all_namespaces()
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
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, cluster.token)
    try:
        statefulsets = apps_v1.list_stateful_set_for_all_namespaces()
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
    apps_v1 = get_apps_client(cluster.api_server, cluster.port, cluster.token)
    try:
        replicasets = apps_v1.list_replica_set_for_all_namespaces()
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