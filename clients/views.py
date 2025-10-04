from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, TemplateView
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Client
from schedules.models import Schedule


class ClientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List view for clients (supervisors only)"""
    model = Client
    template_name = 'clients/list.html'
    context_object_name = 'clients'
    
    def test_func(self):
        return self.request.user.is_supervisor


class ClientScheduleView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Client view of their assigned schedules"""
    template_name = 'clients/my_schedules.html'
    
    def test_func(self):
        return self.request.user.is_client
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current month or specified month
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        
        context['current_year'] = year
        context['current_month'] = month
        context['month_name'] = datetime(year, month, 1).strftime('%B %Y')
        
        # Get schedules for this client
        month_start = datetime(year, month, 1).date()
        month_end = (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_end = month_end.date()
        
        schedules = Schedule.objects.filter(
            client__name=self.request.user.get_full_name(),
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('employee', 'client').order_by('start_date', 'start_time')
        
        context['schedules'] = schedules
        
        # Calculate hours by employee
        hours_by_employee = {}
        for schedule in schedules.filter(status='approved'):
            employee_name = schedule.employee.get_full_name()
            if employee_name not in hours_by_employee:
                hours_by_employee[employee_name] = 0
            hours_by_employee[employee_name] += schedule.duration_hours
        
        context['hours_by_employee'] = hours_by_employee
        
        return context


class ClientReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Client reports view"""
    template_name = 'clients/reports.html'
    
    def test_func(self):
        return self.request.user.is_client
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        # Get schedules for this client
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