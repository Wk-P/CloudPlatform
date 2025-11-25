from django.urls import path
from .views import K8sLoginView, RegisterView, LoginView, MeView, K8sAccountView, SAInfoView, UpdateSATokenView, BindK8sAccountToClusterView

urlpatterns = [
    path('jwt/issue/', K8sLoginView.as_view(), name='jwt_issue'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('me/', MeView.as_view(), name='auth_me'),
    path('k8s/account/', K8sAccountView.as_view(), name='auth_k8s_account'),
    path('k8s/account/bind/', BindK8sAccountToClusterView.as_view(), name='auth_k8s_account_bind'),
    path('k8s/sa-info/', SAInfoView.as_view(), name='auth_k8s_sa_info'),
    path('sa-token/update/', UpdateSATokenView.as_view(), name='auth_update_sa_token'),
]
