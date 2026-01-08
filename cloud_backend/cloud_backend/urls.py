"""
cloud_backend URL configuration
All API routes are grouped by app, with clear prefixes and consistent style.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Anomaly Detection API (DetectorView)
    path('api/anomaly/', include('anomaly_detection.urls')),

    # Authentication API (login/register/me/k8s account)
    path('api/auth/', include('authentication.urls')),

    # Runtime Monitoring API (cluster/node/pod/service/events etc.)
    path('api/runtime/', include('runtime_monitoring.urls')),

    # State Manager API (resource usage, command runner)
    path('api/state/', include('state_manager.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
