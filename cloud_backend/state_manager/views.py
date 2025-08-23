import json
from json import JSONDecodeError
import subprocess
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from runtime_monitoring.models import KubeCluster
from .models import CommandRecord

from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
from kubernetes.client import ApiClient
try:
    import yaml  # optional, for YAML manifests
except Exception:  # pragma: no cover
    yaml = None
from authentication.jwt_utils import jwt_required
from django.conf import settings


ALLOWED_ACTIONS = {"get", "describe", "logs", "apply", "delete", "scale"}


def _configure_k8s(cluster: KubeCluster):
    configuration = client.Configuration()
    configuration.host = f"https://{cluster.api_server}:{cluster.port}"
    tls = getattr(settings, 'K8S_TLS', {}) or {}
    verify = tls.get('VERIFY_SSL', False)
    configuration.verify_ssl = verify
    ca = tls.get('CA_CERT')
    if verify and ca:
        configuration.ssl_ca_cert = ca
    configuration.api_key = {"authorization": "Bearer " + cluster.token}
    client.Configuration.set_default(configuration)


def _truncate(s: str, limit: int = 20000) -> str:
    if s is None:
        return ""
    return s if len(s) <= limit else (s[:limit] + "\n...truncated...")


# Send commands to k8s via SDK (allowlist)
@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def run_command(request):
    try:
        try:
            data = json.loads(request.body or b"{}")
        except JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        action = (data.get("action") or "").lower().strip()
        cluster_id = data.get("cluster_id")
        namespace = data.get("namespace")
        resource = data.get("resource")  # pods, services, deployments, etc.
        name = data.get("name")  # optional, for single resource
        tail_lines = data.get("tail_lines")  # for logs
        manifest = data.get("manifest")  # for apply: str(yaml) | dict | list
        kind = data.get("kind")  # for delete/apply without manifest
        replicas = data.get("replicas")  # for scale

        if action not in ALLOWED_ACTIONS:
            return JsonResponse({"error": f"Unsupported action: {action}"}, status=400)
        if not cluster_id:
            return JsonResponse({"error": "cluster_id is required"}, status=400)
        # per-action validations
        if action == "get" and not resource:
            return JsonResponse({"error": "resource is required for get"}, status=400)
        if action in {"describe", "logs"} and not resource:
            return JsonResponse({"error": "resource is required for describe/logs"}, status=400)
        if action == "scale" and resource and resource != "deployments":
            return JsonResponse({"error": "scale only supports resource 'deployments'"}, status=400)

        # resolve cluster by numeric id or by cluster_id field
        cluster = None
        try:
            if isinstance(cluster_id, int) or (isinstance(cluster_id, str) and str(cluster_id).isdigit()):
                cluster = KubeCluster.objects.get(id=int(cluster_id))
            else:
                cluster = KubeCluster.objects.get(cluster_id=str(cluster_id))
        except KubeCluster.DoesNotExist:
            return JsonResponse({"error": "Cluster not found"}, status=404)

        # persist record after validation
        record = CommandRecord.objects.create(
            cluster_id=str(cluster_id),
            command=json.dumps(data, ensure_ascii=False),
            status='running',
            user=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
        )

        _configure_k8s(cluster)

        stdout = ""
        stderr = ""
        rc = 0

        try:
            # map resources
            v1 = client.CoreV1Api()
            apps = client.AppsV1Api()
            dyn = DynamicClient(ApiClient())

            if action == "get":
                if resource == "pods":
                    resp = v1.list_namespaced_pod(namespace) if namespace else v1.list_pod_for_all_namespaces()
                    items = []
                    for i in resp.items:
                        restarts = 0
                        try:
                            statuses = i.status.container_statuses or []
                            restarts = sum([(cs.restart_count or 0) for cs in statuses])
                        except Exception:
                            restarts = 0
                        created = None
                        try:
                            if i.metadata and i.metadata.creation_timestamp:
                                created = i.metadata.creation_timestamp.isoformat()
                        except Exception:
                            created = None
                        items.append({
                            "ns": getattr(i.metadata, 'namespace', ''),
                            "name": getattr(i.metadata, 'name', ''),
                            "status": getattr(i.status, 'phase', ''),
                            "node": getattr(i.spec, 'node_name', ''),
                            "ip": getattr(i.status, 'pod_ip', ''),
                            "restarts": restarts,
                            "created_at": created,
                        })
                    stdout = json.dumps(items)
                elif resource == "services":
                    resp = v1.list_namespaced_service(namespace) if namespace else v1.list_service_for_all_namespaces()
                    items = []
                    for i in resp.items:
                        ports = []
                        try:
                            for p in (i.spec.ports or []):
                                ports.append(f"{p.port}/{p.protocol}")
                        except Exception:
                            ports = []
                        items.append({
                            "ns": getattr(i.metadata, 'namespace', ''),
                            "name": getattr(i.metadata, 'name', ''),
                            "type": getattr(i.spec, 'type', ''),
                            "cluster_ip": getattr(i.spec, 'cluster_ip', '') or getattr(i.spec, 'clusterIPs', None),
                            "ports": ports,
                        })
                    stdout = json.dumps(items)
                elif resource == "deployments":
                    resp = apps.list_namespaced_deployment(namespace) if namespace else apps.list_deployment_for_all_namespaces()
                    items = []
                    for i in resp.items:
                        items.append({
                            "ns": getattr(i.metadata, 'namespace', ''),
                            "name": getattr(i.metadata, 'name', ''),
                            "replicas": getattr(i.status, 'replicas', 0),
                            "ready": getattr(i.status, 'ready_replicas', 0),
                            "updated": getattr(i.status, 'updated_replicas', 0),
                            "available": getattr(i.status, 'available_replicas', 0),
                        })
                    stdout = json.dumps(items)
                else:
                    stderr = f"Unsupported resource for get: {resource}"
                    rc = 2

            elif action == "describe":
                if not name:
                    stderr = "name is required for describe"
                    rc = 2
                elif resource == "pods":
                    obj = v1.read_namespaced_pod(name=name, namespace=namespace or 'default')
                    stdout = json.dumps({
                        "ns": obj.metadata.namespace,
                        "name": obj.metadata.name,
                        "node": obj.spec.node_name,
                        "status": obj.status.phase,
                        "containers": [c.name for c in (obj.spec.containers or [])]
                    })
                elif resource == "deployments":
                    obj = apps.read_namespaced_deployment(name=name, namespace=namespace or 'default')
                    stdout = json.dumps({
                        "ns": obj.metadata.namespace,
                        "name": obj.metadata.name,
                        "replicas": obj.status.replicas,
                        "ready": obj.status.ready_replicas,
                    })
                else:
                    stderr = f"Unsupported resource for describe: {resource}"
                    rc = 2

            elif action == "logs":
                if resource != "pods":
                    stderr = "logs only supports resource 'pods'"
                    rc = 2
                elif not name:
                    stderr = "name is required for logs"
                    rc = 2
                else:
                    stdout = v1.read_namespaced_pod_log(name=name, namespace=namespace or 'default', tail_lines=tail_lines)

            elif action == "apply":
                if manifest is None:
                    stderr = "manifest is required for apply"
                    rc = 2
                else:
                    objects = []
                    try:
                        if isinstance(manifest, str):
                            if yaml is None:
                                raise RuntimeError("PyYAML not installed; send JSON manifest instead")
                            for doc in yaml.safe_load_all(manifest):
                                if doc:
                                    objects.append(doc)
                        elif isinstance(manifest, dict):
                            objects = [manifest]
                        elif isinstance(manifest, list):
                            objects = [o for o in manifest if isinstance(o, dict)]
                        else:
                            raise ValueError("manifest must be YAML string, object, or list")
                    except Exception as ex:
                        stderr = f"Failed to parse manifest: {ex}"
                        rc = 2
                        objects = []

                    results = []
                    if rc == 0:
                        if not objects:
                            stderr = "No manifest objects parsed. Ensure YAML has proper line breaks/indentation or pass valid JSON."
                            rc = 2
                        
                        for obj in objects:
                            try:
                                api_version = obj.get('apiVersion')
                                k = obj.get('kind')
                                meta = obj.get('metadata') or {}
                                nm = meta.get('name')
                                ns = meta.get('namespace')
                                if not (api_version and k and nm):
                                    raise ValueError("Each manifest requires apiVersion, kind, metadata.name")
                                res = dyn.resources.get(api_version=api_version, kind=k)
                                try:
                                    res.patch(name=nm, namespace=ns, body=obj, content_type='application/apply-patch+yaml', field_manager='cloud-platform', force=True)
                                    results.append({"kind": k, "ns": ns, "name": nm, "action": "applied"})
                                except Exception:
                                    try:
                                        res.create(body=obj, namespace=ns)
                                        results.append({"kind": k, "ns": ns, "name": nm, "action": "created"})
                                    except Exception as ex2:
                                        results.append({"kind": k, "ns": ns, "name": nm, "error": str(ex2)})
                                        rc = 1
                            except Exception as ex:
                                results.append({"error": str(ex)})
                                rc = 1
                    stdout = json.dumps(results, ensure_ascii=False)

            elif action == "delete":
                target_kind = kind
                if not target_kind and resource:
                    mapping = {
                        'pods': 'Pod', 'services': 'Service', 'deployments': 'Deployment',
                        'daemonsets': 'DaemonSet', 'statefulsets': 'StatefulSet', 'replicasets': 'ReplicaSet',
                        'configmaps': 'ConfigMap', 'secrets': 'Secret', 'ingresses': 'Ingress', 'namespaces': 'Namespace'
                    }
                    target_kind = mapping.get(str(resource).lower())
                if not (target_kind and name):
                    stderr = "kind/resource and name are required for delete"
                    rc = 2
                else:
                    api_groups = [
                        ('v1', {'Namespace','Pod','Service','ConfigMap','Secret'}),
                        ('apps/v1', {'Deployment','StatefulSet','DaemonSet','ReplicaSet'}),
                        ('networking.k8s.io/v1', {'Ingress'}),
                    ]
                    deleted = False
                    err = None
                    for api_version, kinds in api_groups:
                        if target_kind in kinds:
                            try:
                                res = dyn.resources.get(api_version=api_version, kind=target_kind)
                                # cluster-scoped
                                if hasattr(res, 'namespaced') and not res.namespaced:
                                    res.delete(name=name)
                                else:
                                    res.delete(name=name, namespace=namespace or 'default')
                                deleted = True
                                break
                            except Exception as ex:
                                err = ex
                                continue
                    if deleted:
                        stdout = json.dumps({"kind": target_kind, "name": name, "ns": namespace, "action": "deleted"})
                    else:
                        stderr = f"Delete failed for {target_kind}/{namespace}/{name}: {err}"
                        rc = 1

            elif action == "scale":
                if not name or replicas is None:
                    stderr = "name and replicas are required for scale"
                    rc = 2
                else:
                    try:
                        body = {"spec": {"replicas": int(replicas)}}
                    except Exception:
                        stderr = "replicas must be an integer"
                        rc = 2
                    if rc == 0:
                        apps.patch_namespaced_deployment_scale(
                            name=name,
                            namespace=namespace or 'default',
                            body=body
                        )
                        stdout = json.dumps({
                            "resource": "deployments",
                            "name": name,
                            "ns": namespace or 'default',
                            "replicas": int(replicas),
                            "action": "scaled"
                        })

        except Exception as ex:
            stderr = str(ex)
            rc = 1

        # update record
        record.stdout = _truncate(stdout)
        record.stderr = _truncate(stderr)
        record.returncode = rc
        record.status = 'done' if rc == 0 else 'failed'
        record.save()

        return JsonResponse({
            "record_id": record.id,
            "stdout": record.stdout,
            "stderr": record.stderr,
            "returncode": record.returncode,
            "status": record.status
        })
    except Exception as e:
        # unexpected error
        return JsonResponse({"error": str(e)}, status=500)


def get_cluster_usage(request, id: int):
    """Get cluster usage by cluster primary key id."""
    cluster = get_object_or_404(KubeCluster, id=id)
    configuration = client.Configuration()
    configuration.host = f"https://{cluster.api_server}:{cluster.port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + cluster.token}
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    metrics = client.CustomObjectsApi()

    total_cpu = 0
    used_cpu = 0
    total_mem = 0
    used_mem = 0

    # capacity
    nodes = v1.list_node()
    for node in nodes.items:
        cpu = node.status.capacity['cpu']
        mem = node.status.capacity['memory']

        total_cpu += int(cpu)
        mem_mi = int(mem.replace('Ki', '')) // 1024
        total_mem += mem_mi

    # usage
    node_metrics = metrics.list_cluster_custom_object(
        group="metrics.k8s.io", version="v1beta1", plural="nodes"
    )
    for item in node_metrics['items']:
        cpu = item['usage']['cpu']
        mem = item['usage']['memory']

        if cpu.endswith('n'):
            used_cpu += int(cpu[:-1]) / 1_000_000_000
        elif cpu.endswith('m'):
            used_cpu += int(cpu[:-1]) / 1000

        if mem.endswith('Ki'):
            used_mem += int(mem[:-2]) // 1024

    return JsonResponse({
        "total_cpu": f"{total_cpu} cores",
        "used_cpu": f"{used_cpu:.2f} cores",
        "cpu_utilization": f"{used_cpu/total_cpu*100:.2f}%",
        "total_memory": f"{total_mem} Mi",
        "used_memory": f"{used_mem} Mi",
        "memory_utilization": f"{used_mem/total_mem*100:.2f}%",
    })


def get_node_usage(request, id, node_name):
    cluster = get_object_or_404(KubeCluster, id=id)
    configuration = client.Configuration()
    configuration.host = f"https://{cluster.api_server}:{cluster.port}"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + cluster.token}
    client.Configuration.set_default(configuration)

    v1 = client.CoreV1Api()
    metrics = client.CustomObjectsApi()

    # capacity
    node = v1.read_node(node_name)
    cpu = int(node.status.capacity['cpu'])
    mem_mi = int(node.status.capacity['memory'].replace('Ki', '')) // 1024

    # usage
    node_metrics = metrics.get_cluster_custom_object(
        group="metrics.k8s.io", version="v1beta1", plural="nodes", name=node_name
    )

    cpu_usage = node_metrics['usage']['cpu']
    mem_usage = node_metrics['usage']['memory']

    # cpu usage
    cpu_u = 0
    if cpu_usage.endswith('n'):
        cpu_u = int(cpu_usage[:-1]) / 1_000_000_000
    elif cpu_usage.endswith('m'):
        cpu_u = int(cpu_usage[:-1]) / 1000

    # memory usage
    mem_u = 0
    if mem_usage.endswith('Ki'):
        mem_u = int(mem_usage[:-2]) // 1024

    return JsonResponse({
        "name": node_name,
        "total_cpu": f"{cpu} cores",
        "used_cpu": f"{cpu_u:.2f} cores",
        "cpu_utilization": f"{cpu_u / cpu * 100:.2f}%",
        "total_memory": f"{mem_mi} Mi",
        "used_memory": f"{mem_u} Mi",
        "memory_utilization": f"{mem_u / mem_mi * 100:.2f}%"
    })


@require_http_methods(["GET"])
def get_command_result(request, id: int):
    record = get_object_or_404(CommandRecord, id=id)
    return JsonResponse({
        "record_id": record.id,
        "stdout": record.stdout,
        "stderr": record.stderr,
        "returncode": record.returncode,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })
