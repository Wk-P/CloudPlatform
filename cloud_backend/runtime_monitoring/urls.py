from django.urls import path
import runtime_monitoring.views as rm_views

urlpatterns = [

    # cluster
    path('clusters/baseinfo/', rm_views.get_clusters_base_info_list, name='get_clusters_ids'),
    path('clusters/<int:id>/cluster/', rm_views.get_cluster_info, name='get_cluster'),
    
    # base resources
    path('cluster/add/', rm_views.add_cluster_simple, name='add_cluster'),
    path('cluster/<int:id>/nodes/', rm_views.get_nodes, name='get_nodes'),
    path('cluster/<int:id>/pods/', rm_views.get_pods, name='get_pods'),
    path('cluster/<int:id>/services/', rm_views.get_services, name='get_services'),
    path('cluster/<int:id>/events/', rm_views.get_events, name='get_events'),

    # apps
    path('cluster/<int:id>/deployments/', rm_views.get_deployments, name='get_deployments'),
    path('cluster/<int:id>/daemonsets/', rm_views.get_daemonsets, name='get_daemonsets'),
    path('cluster/<int:id>/statefulsets/', rm_views.get_statefulsets, name='get_statefulsets'),
    path('cluster/<int:id>/replicasets/', rm_views.get_replicasets, name='get_replicasets'),

    # batch
    path('cluster/<int:id>/jobs/', rm_views.get_jobs, name='get_jobs'),

    # more
]