from django.urls import path
import runtime_monitoring.views as rm_views

urlpatterns = [

    # cluster
    path('clusters/baseinfo/', rm_views.get_clusters_base_info_list, name='get_clusters_ids'),
    path('clusters/<int:id>/cluster/', rm_views.get_cluster_info, name='get_cluster'),
    
    # base resources
    path('clusters/add/', rm_views.add_cluster_simple, name='add_cluster'),
    path('clusters/<int:id>/nodes/', rm_views.get_nodes, name='get_nodes'),
    path('clusters/<int:id>/pods/', rm_views.get_pods, name='get_pods'),
    path('clusters/<int:id>/services/', rm_views.get_services, name='get_services'),
    path('clusters/<int:id>/events/', rm_views.get_events, name='get_events'),
    path('clusters/<int:id>/namespaces/', rm_views.get_namespaces, name='get_namespaces'),

    # apps
    path('clusters/<int:id>/deployments/', rm_views.get_deployments, name='get_deployments'),
    path('clusters/<int:id>/daemonsets/', rm_views.get_daemonsets, name='get_daemonsets'),
    path('clusters/<int:id>/statefulsets/', rm_views.get_statefulsets, name='get_statefulsets'),
    path('clusters/<int:id>/replicasets/', rm_views.get_replicasets, name='get_replicasets'),

    # batch
    path('clusters/<int:id>/jobs/', rm_views.get_jobs, name='get_jobs'),

    # more
]