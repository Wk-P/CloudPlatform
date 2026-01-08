from django.contrib import admin
from .models import ManagerCustomUser, K8sAccount, OtherAccount


@admin.register(ManagerCustomUser)
class ManagerCustomUserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'uuid')
    readonly_fields = ('uuid', 'date_joined', 'last_login')
    fieldsets = (
        ('基本信息', {'fields': ('uuid', 'username', 'email')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('时间信息', {'fields': ('date_joined', 'last_login')}),
    )


@admin.register(K8sAccount)
class K8sAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cluster_name', 'namespace', 'token_expire_time')
    list_filter = ('cluster_name', 'namespace')
    search_fields = ('user__username', 'cluster_name', 'namespace')
    readonly_fields = ('token_expire_time',)
    fieldsets = (
        ('用户信息', {'fields': ('user', 'cluster', 'cluster_name')}),
        ('Kubernetes 配置', {'fields': ('namespace', 'k8s_api_server_url', 'kubeconfig')}),
        ('Token 信息', {'fields': ('token', 'token_expire_time', 'user_group')}),
    )


@admin.register(OtherAccount)
class OtherAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cluster_name', 'cluster_id')
    search_fields = ('user__username', 'cluster_name', 'cluster_id')
