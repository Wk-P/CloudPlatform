from django.urls import path
from . import views

urlpatterns = [
    # endpoints for DetectorView
    path('ingress/blacklist/', views.ingress_blacklist, name='ingress-blacklist'),
    path('ingress/traffic/trend/', views.ingress_traffic_trend, name='ingress-traffic-trend'),

    path('ingress/redis/data/read/', views.ingress_redis_data_read, name='ingress-redis-data-read'),
]
