import json
import subprocess
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from runtime_monitoring.models import KubeCluster
from .models import CommandRecord

from kubernetes import client, config


# Send commands to k8s and 
@csrf_exempt 
@require_http_methods(["POST"])
def run_command(request):
    try:
        data = json.loads(request.body)
        cmd = data.get("cmd")
        # cluster_id = data.get("cluster_id", "")

        # if not cmd:
        #     return JsonResponse({"error": "No command provided"}, status=400)

        # # only kubectl command
        # if not cmd.startswith("kubectl"):
        #     return JsonResponse({"error": "Only kubectl commands are allowed"}, status=400)

        # # write into db, pending status
        # record = CommandRecord.objects.create(
        #     cluster_id=cluster_id,
        #     command=cmd,
        #     status='running',
        #     user=request.user if request.user.is_authenticated else None
        # )

        # run
        # result = subprocess.run(
        #     cmd.split(),
        #     capture_output=True,
        #     text=True
        # )

        # # update db
        # record.stdout = result.stdout
        # record.stderr = result.stderr
        # record.returncode = result.returncode
        # record.status = 'done' if result.returncode == 0 else 'failed'
        # record.save()

        # return
        # return JsonResponse({
        #     "record_id": record.id,
        #     "stdout": result.stdout,
        #     "stderr": result.stderr,
        #     "returncode": result.returncode,
        #     "status": record.status
        # })

        return JsonResponse({
            "record_id": "test 002a2",
            "stdout": "test stdout",
            "stderr": "test stderror",
            "returncode": 200,
            "status": "test finish"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_cluster_usage(request, id):
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
