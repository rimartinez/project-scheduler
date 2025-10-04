from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
from schedules.models import Schedule
from clients.models import Client
from accounts.models import User


class ReportsIndexView(LoginRequiredMixin, TemplateView):
    """Main reports index view"""
    template_name = 'reports/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from filters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        status_filter = self.request.GET.get('status')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()
        
        # Get schedules based on user role and filters
        schedules = Schedule.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('employee', 'client', 'approved_by')
        
        if self.request.user.is_employee:
            schedules = schedules.filter(employee=self.request.user)
        elif self.request.user.is_client:
            schedules = schedules.filter(client__name=self.request.user.get_full_name())
        
        if status_filter:
            schedules = schedules.filter(status=status_filter)
        
        # Calculate summary statistics
        total_schedules = schedules.count()
        approved_schedules = schedules.filter(status='approved').count()
        pending_schedules = schedules.filter(status__in=['submitted', 'draft']).count()
        total_hours = sum(schedule.duration_hours for schedule in schedules.filter(status='approved'))
        
        # Status distribution
        status_distribution = {}
        for status, _ in Schedule.STATUS_CHOICES:
            count = schedules.filter(status=status).count()
            if count > 0:
                status_distribution[status] = count
        
        # Monthly hours (last 6 months)
        monthly_hours = {}
        for i in range(6):
            month_date = datetime.now().date().replace(day=1) - timedelta(days=30*i)
            month_schedules = schedules.filter(
                start_date__year=month_date.year,
                start_date__month=month_date.month,
                status='approved'
            )
            month_hours = sum(schedule.duration_hours for schedule in month_schedules)
            if month_hours > 0:
                monthly_hours[month_date.strftime('%B %Y')] = month_hours
        
        # Recent schedules (last 10)
        recent_schedules = schedules.order_by('-created_at')[:10]
        
        context.update({
            'user_role': self.request.user.role,
            'total_schedules': total_schedules,
            'approved_schedules': approved_schedules,
            'pending_schedules': pending_schedules,
            'total_hours': total_hours,
            'status_distribution': status_distribution,
            'monthly_hours': monthly_hours,
            'recent_schedules': recent_schedules,
        })
        
        return context


class EmployeeReportsView(LoginRequiredMixin, TemplateView):
    """Employee reports view"""
    template_name = 'reports/employee.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get employee's schedules
        schedules = Schedule.objects.filter(
            employee=self.request.user,
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('client')
        
        context['schedules'] = schedules
        context['total_hours'] = sum(schedule.duration_hours for schedule in schedules.filter(status='approved'))
        
        # Hours by client
        hours_by_client = {}
        for schedule in schedules.filter(status='approved'):
            client_name = schedule.client.name
            if client_name not in hours_by_client:
                hours_by_client[client_name] = 0
            hours_by_client[client_name] += schedule.duration_hours
        
        context['hours_by_client'] = hours_by_client
        
        # Status breakdown
        status_breakdown = {}
        for status, _ in Schedule.STATUS_CHOICES:
            count = schedules.filter(status=status).count()
            status_breakdown[status] = count
        
        context['status_breakdown'] = status_breakdown
        
        return context


class ClientReportsView(LoginRequiredMixin, TemplateView):
    """Client reports view"""
    template_name = 'reports/client.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get client's schedules
        schedules = Schedule.objects.filter(
            client__name=self.request.user.get_full_name(),
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('employee', 'client')
        
        context['schedules'] = schedules
        context['total_hours'] = sum(schedule.duration_hours for schedule in schedules.filter(status='approved'))
        
        # Hours by employee
        hours_by_employee = {}
        for schedule in schedules.filter(status='approved'):
            employee_name = schedule.employee.get_full_name()
            if employee_name not in hours_by_employee:
                hours_by_employee[employee_name] = 0
            hours_by_employee[employee_name] += schedule.duration_hours
        
        context['hours_by_employee'] = hours_by_employee
        
        return context


class SupervisorReportsView(LoginRequiredMixin, TemplateView):
    """Supervisor reports view"""
    template_name = 'reports/supervisor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get all schedules
        schedules = Schedule.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('employee', 'client', 'approved_by')
        
        context['schedules'] = schedules
        context['total_hours'] = sum(schedule.duration_hours for schedule in schedules.filter(status='approved'))
        
        # Employee performance
        employee_stats = schedules.values('employee__first_name', 'employee__last_name').annotate(
            total_schedules=Count('id'),
            approved_schedules=Count('id', filter=Q(status='approved')),
            pending_schedules=Count('id', filter=Q(status='submitted')),
            rejected_schedules=Count('id', filter=Q(status='rejected')),
        ).order_by('-total_schedules')
        
        context['employee_stats'] = employee_stats
        
        # Status breakdown
        status_breakdown = {}
        for status, _ in Schedule.STATUS_CHOICES:
            count = schedules.filter(status=status).count()
            status_breakdown[status] = count
        
        context['status_breakdown'] = status_breakdown
        
        # Client distribution
        client_stats = schedules.values('client__name').annotate(
            total_schedules=Count('id'),
            approved_schedules=Count('id', filter=Q(status='approved')),
        ).order_by('-total_schedules')
        
        context['client_stats'] = client_stats
        
        return context


class ExportReportsView(LoginRequiredMixin, TemplateView):
    """Export reports view"""
    template_name = 'reports/export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get export type
        export_type = self.request.GET.get('type', 'csv')
        context['export_type'] = export_type
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle export requests"""
        export_type = request.POST.get('type', 'csv')
        date_range = request.POST.get('date_range', '30')
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=int(date_range))
        
        # Get schedules based on user role
        if request.user.is_employee:
            schedules = Schedule.objects.filter(
                employee=request.user,
                start_date__gte=start_date,
                start_date__lte=end_date
            ).select_related('client')
        elif request.user.is_client:
            schedules = Schedule.objects.filter(
                client__name=request.user.get_full_name(),
                start_date__gte=start_date,
                start_date__lte=end_date
            ).select_related('employee', 'client')
        else:  # supervisor
            schedules = Schedule.objects.filter(
                start_date__gte=start_date,
                start_date__lte=end_date
            ).select_related('employee', 'client', 'approved_by')
        
        if export_type == 'csv':
            return self.export_csv(schedules)
        elif export_type == 'excel':
            return self.export_excel(schedules)
        else:
            return HttpResponse('Invalid export type', status=400)
    
    def export_csv(self, schedules):
        """Export schedules as CSV"""
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="schedules.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Start Time', 'End Time', 'Client', 'Employee', 'Status', 'Hours', 'Notes'])
        
        for schedule in schedules:
            writer.writerow([
                schedule.start_date,
                schedule.start_time,
                schedule.end_time,
                schedule.client.name,
                schedule.employee.get_full_name(),
                schedule.get_status_display(),
                schedule.duration_hours,
                schedule.notes or '',
            ])
        
        return response
    
    def export_excel(self, schedules):
        """Export schedules as Excel"""
        # This would require openpyxl or xlsxwriter
        # For now, return CSV
        return self.export_csv(schedules)