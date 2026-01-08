import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from authentication.jwt_utils import jwt_required
from .models import IngressBlacklistItem, IngressTrafficSample
import requests

@jwt_required
@require_http_methods(["GET"])
def ingress_blacklist(_request):
	items = list(IngressBlacklistItem.objects.order_by('-updated_at').values(
		"source", "ip", "cidr", "pattern",
		"action", "mode", "control",
		"scope", "target",
		"reason", "note", "updated_at"
	)[:500])
	# normalize datetime to isoformat
	for it in items:
		if it.get("updated_at"):
			it["updated_at"] = it["updated_at"].isoformat()
	return JsonResponse({"items": items})


@jwt_required
@require_http_methods(["GET"])
def ingress_traffic_trend(request):
	limit = 120
	try:
		if request.GET.get('limit'):
			limit = max(1, min(2000, int(request.GET['limit'])))
	except Exception:
		limit = 120
	qs = IngressTrafficSample.objects.order_by('-ts')[:limit]
	points = [{
		"ts": s.ts.isoformat(),
		"value": s.value,
	} for s in qs]
	# reverse to ascending by time for display
	points.reverse()
	return JsonResponse({"points": points})


@jwt_required
@require_http_methods(["GET"])
def ingress_redis_data_read(request):
    from runtime_monitoring.models import KubeCluster
    from authentication.jwt_utils import jwt_decode
    from authentication.models import ManagerCustomUser, K8sAccount
    
    # Get current user's cluster from request or default to first cluster
    cluster_id = request.GET.get('cluster_id')
    
    if cluster_id:
        try:
            cluster = KubeCluster.objects.get(id=cluster_id)
        except KubeCluster.DoesNotExist:
            return JsonResponse({"error": "Cluster not found"}, status=404)
    else:
        # Try to get cluster from user's K8sAccount binding
        auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if auth and auth.startswith('Bearer '):
            try:
                payload = jwt_decode(auth.split(' ', 1)[1])
                user = ManagerCustomUser.objects.get(uuid=payload.get('sub'))
                k8s_acc = K8sAccount.objects.filter(user=user).order_by('-id').first()
                if k8s_acc and k8s_acc.cluster:
                    cluster = k8s_acc.cluster
                else:
                    cluster = KubeCluster.objects.first()
            except Exception:
                cluster = KubeCluster.objects.first()
        else:
            cluster = KubeCluster.objects.first()
    
    if not cluster:
        return JsonResponse({"error": "No cluster configured"}, status=400)
    
    if not cluster.redis_report_endpoint:
        return JsonResponse({
            "error": "Redis report endpoint not configured for this cluster",
            "cluster": cluster.name
        }, status=400)
    
    try:
        response = requests.get(cluster.redis_report_endpoint, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({"data": data})
        return JsonResponse({
            "error": f"Redis service returned status {response.status_code}",
            "details": response.text[:200]
        }, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "error": "Failed to connect to Redis report service",
            "details": str(e)
        }, status=503)