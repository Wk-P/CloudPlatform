from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ManagerCustomUser
from .jwt_utils import jwt_encode

# Create your views here.
class K8sLoginView(APIView):
    def post(self, request: Request):
        # Minimal issue-only JWT for experimental usage
        # Accept either username or anonymous client id
        username = request.data.get('username') or 'anonymous'
        user, _ = ManagerCustomUser.objects.get_or_create(username=username, defaults={'password': '!'})
        token = jwt_encode({'sub': str(user.uuid), 'username': user.username})
        return Response({'token': token})