from django.urls import path
from state_manager import views as sm_views

urlpatterns = [
    path("run/cmd/", sm_views.run_command, name="run_command"),
    path("resources/cluster/<int:id>/", sm_views.get_cluster_usage, name="get_cluster_usage")
]
