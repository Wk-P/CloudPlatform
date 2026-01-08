from django.contrib import admin
from .models import KubeCluster


@admin.register(KubeCluster)
class KubeClusterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'api_server', 'port', 'cluster_id')
    search_fields = ('name', 'api_server', 'description', 'cluster_id')
    fieldsets = (
        ('集群信息', {'fields': ('name', 'api_server', 'port', 'cluster_id', 'description')}),
    )
