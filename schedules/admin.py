from django.contrib import admin
from django.utils.html import format_html
from .models import Schedule, ScheduleConflict


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Schedule admin configuration"""
    
    list_display = ('employee', 'client', 'start_date', 'start_time', 'end_date', 'end_time', 'status_badge', 'duration_hours', 'created_at')
    list_filter = ('status', 'employee__role', 'client', 'start_date', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'client__name', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('employee', 'client', 'start_date', 'start_time', 'end_date', 'end_time', 'notes')
        }),
        ('Status & Approval', {
            'fields': ('status', 'submitted_at', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'approved_at')
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': 'gray',
            'submitted': 'yellow',
            'approved': 'green',
            'rejected': 'red',
            'modified': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'client', 'approved_by')
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only based on user role"""
        readonly_fields = list(self.readonly_fields)
        
        # Only supervisors can change status
        if not request.user.is_superuser and not request.user.is_supervisor:
            readonly_fields.extend(['status', 'approved_by', 'approved_at', 'rejection_reason'])
        
        return readonly_fields


@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    """Schedule Conflict admin configuration"""
    
    list_display = ('schedule', 'conflicting_schedule', 'conflict_type', 'created_at')
    list_filter = ('conflict_type', 'created_at')
    search_fields = ('schedule__employee__first_name', 'schedule__employee__last_name', 'schedule__client__name')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'schedule__employee', 'schedule__client',
            'conflicting_schedule__employee', 'conflicting_schedule__client'
        )