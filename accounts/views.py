from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import User
from schedules.models import Schedule
from clients.models import Client


class LoginView(BaseLoginView):
    """Custom login view with role-based redirect"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name()}!')
        return super().form_valid(form)


class LogoutView(TemplateView):
    """Custom logout view"""
    template_name = 'accounts/logout.html'
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class RegisterView(FormView):
    """User registration view"""
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard')
    
    def get_form_class(self):
        from .forms import UserRegistrationForm
        return UserRegistrationForm
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with role-based content"""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get current month data
        now = datetime.now()
        month_start = now.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        if user.is_employee:
            context.update(self.get_employee_dashboard_data(user, month_start, month_end))
        elif user.is_supervisor:
            context.update(self.get_supervisor_dashboard_data(user, month_start, month_end))
        elif user.is_client:
            context.update(self.get_client_dashboard_data(user, month_start, month_end))
        
        return context
    
    def get_employee_dashboard_data(self, user, month_start, month_end):
        """Get dashboard data for employees"""
        schedules = Schedule.objects.filter(
            employee=user,
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('client')
        
        # Statistics
        total_schedules = schedules.count()
        approved_schedules = schedules.filter(status='approved').count()
        pending_schedules = schedules.filter(status='submitted').count()
        rejected_schedules = schedules.filter(status='rejected').count()
        
        # Recent schedules
        recent_schedules = schedules.order_by('-created_at')[:5]
        
        # Hours by client
        hours_by_client = {}
        for schedule in schedules.filter(status='approved'):
            client_name = schedule.client.name
            if client_name not in hours_by_client:
                hours_by_client[client_name] = 0
            hours_by_client[client_name] += schedule.duration_hours
        
        return {
            'total_schedules': total_schedules,
            'approved_schedules': approved_schedules,
            'pending_schedules': pending_schedules,
            'rejected_schedules': rejected_schedules,
            'recent_schedules': recent_schedules,
            'hours_by_client': hours_by_client,
            'dashboard_type': 'employee',
        }
    
    def get_supervisor_dashboard_data(self, user, month_start, month_end):
        """Get dashboard data for supervisors"""
        # All schedules in the system
        all_schedules = Schedule.objects.filter(
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('employee', 'client')
        
        # Statistics
        total_schedules = all_schedules.count()
        pending_approvals = all_schedules.filter(status='submitted').count()
        approved_schedules = all_schedules.filter(status='approved').count()
        rejected_schedules = all_schedules.filter(status='rejected').count()
        
        # Recent submissions
        recent_submissions = all_schedules.filter(status='submitted').order_by('-submitted_at')[:5]
        
        # Employee performance
        employee_stats = all_schedules.values('employee__first_name', 'employee__last_name').annotate(
            total_schedules=Count('id'),
            approved_schedules=Count('id', filter=Q(status='approved')),
            pending_schedules=Count('id', filter=Q(status='submitted')),
        ).order_by('-total_schedules')[:5]
        
        return {
            'total_schedules': total_schedules,
            'pending_approvals': pending_approvals,
            'approved_schedules': approved_schedules,
            'rejected_schedules': rejected_schedules,
            'recent_submissions': recent_submissions,
            'employee_stats': employee_stats,
            'dashboard_type': 'supervisor',
        }
    
    def get_client_dashboard_data(self, user, month_start, month_end):
        """Get dashboard data for clients"""
        # Schedules assigned to this client
        schedules = Schedule.objects.filter(
            client__name=user.get_full_name(),  # Assuming client name matches user name
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('employee')
        
        # Statistics
        total_schedules = schedules.count()
        approved_schedules = schedules.filter(status='approved').count()
        pending_schedules = schedules.filter(status='submitted').count()
        
        # Recent schedules
        recent_schedules = schedules.order_by('-created_at')[:5]
        
        # Hours by employee
        hours_by_employee = {}
        for schedule in schedules.filter(status='approved'):
            employee_name = schedule.employee.get_full_name()
            if employee_name not in hours_by_employee:
                hours_by_employee[employee_name] = 0
            hours_by_employee[employee_name] += schedule.duration_hours
        
        return {
            'total_schedules': total_schedules,
            'approved_schedules': approved_schedules,
            'pending_schedules': pending_schedules,
            'recent_schedules': recent_schedules,
            'hours_by_employee': hours_by_employee,
            'dashboard_type': 'client',
        }


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """User settings view"""
    template_name = 'accounts/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context