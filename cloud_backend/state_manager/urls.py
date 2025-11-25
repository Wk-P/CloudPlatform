from django.urls import path
from state_manager import views as sm_views

urlpatterns = [
    path("run/cmd/", sm_views.run_command, name="run_command"),
    path("run/cmd/<int:id>/", sm_views.get_command_result, name="get_command_result"),
    path("resources/cluster/<int:id>/", sm_views.get_cluster_usage, name="get_cluster_usage"),
    path("resources/node/<int:id>/<str:node_name>/", sm_views.get_node_usage, name="get_node_usage")
]
