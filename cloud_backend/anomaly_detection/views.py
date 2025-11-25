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
def ingress_redis_data_read(_request):
    # Implement your logic here
    response = requests.get("http://192.168.0.247:8099/report/read")
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({"data": data})
    return JsonResponse({"error": "Failed to read Redis data"}, status=500)