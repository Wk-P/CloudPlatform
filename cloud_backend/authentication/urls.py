from django.urls import path
from .views import K8sLoginView

urlpatterns = [
    path('auth/jwt/issue/', K8sLoginView.as_view(), name='jwt_issue'),
]
