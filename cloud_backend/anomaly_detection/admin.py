from django.contrib import admin
from .models import IngressBlacklistItem, IngressTrafficSample


@admin.register(IngressBlacklistItem)
class IngressBlacklistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'ip', 'cidr', 'pattern', 'action', 'reason', 'created_at')
    list_filter = ('action', 'mode', 'created_at', 'updated_at')
    search_fields = ('source', 'ip', 'cidr', 'pattern', 'reason', 'note')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('来源信息', {'fields': ('source', 'ip', 'cidr', 'pattern')}),
        ('控制动作', {'fields': ('action', 'mode', 'control')}),
        ('范围目标', {'fields': ('scope', 'target')}),
        ('备注信息', {'fields': ('reason', 'note')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(IngressTrafficSample)
class IngressTrafficSampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'ts', 'value', 'metric', 'scope')
    list_filter = ('metric', 'scope', 'ts')
    search_fields = ('metric', 'scope')
    readonly_fields = ('ts',)
    fieldsets = (
        ('数据点信息', {'fields': ('ts', 'value', 'metric', 'scope')}),
    )
