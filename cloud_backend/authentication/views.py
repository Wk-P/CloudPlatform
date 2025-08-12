from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import ManagerCustomUser, K8sAccount, OtherAccount
from auth import test_https_width_token

# Create your views here.
class K8sLoginView(APIView):
    def post(self, request: Request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': "Username and password is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        # login
        # test_https_width_token()