from django.contrib import admin
from .models import CommandRecord


@admin.register(CommandRecord)
class CommandRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cluster_id', 'command', 'status', 'returncode', 'created_at')
    list_filter = ('status', 'created_at', 'returncode')
    search_fields = ('user__username', 'command', 'cluster_id')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('执行信息', {'fields': ('user', 'cluster_id', 'status')}),
        ('命令详情', {'fields': ('command', 'returncode')}),
        ('输出结果', {'fields': ('stdout', 'stderr')}),
        ('时间信息', {'fields': ('created_at',)}),
    )
