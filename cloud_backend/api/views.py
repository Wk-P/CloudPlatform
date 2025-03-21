from rest_framework.views import APIView
from rest_framework.response import Response
from clusters.models import K8sCluster

# Create your views here.

class K8sClusterListView(APIView):
    def get(self, request):
        clusters = list(K8sCluster.objects.values())
        return Response({"clusters": clusters})
