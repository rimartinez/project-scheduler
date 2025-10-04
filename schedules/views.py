from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Schedule
from .forms import ScheduleForm
from clients.models import Client


class ScheduleListView(LoginRequiredMixin, ListView):
    """List view for schedules with role-based filtering"""
    model = Schedule
    template_name = 'schedules/list.html'
    context_object_name = 'schedules'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Schedule.objects.select_related('employee', 'client', 'approved_by')
        
        if self.request.user.is_employee:
            queryset = queryset.filter(employee=self.request.user)
        elif self.request.user.is_client:
            # For clients, show schedules where they are the client
            queryset = queryset.filter(client__name=self.request.user.get_full_name())
        # Supervisors see all schedules
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.role
        return context


class ScheduleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create view for schedules (employees only)"""
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/create.html'
    success_url = reverse_lazy('schedules:list')
    
    def test_func(self):
        return self.request.user.is_employee
    
    def form_valid(self, form):
        form.instance.employee = self.request.user
        messages.success(self.request, 'Schedule created successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ScheduleDetailView(LoginRequiredMixin, DetailView):
    """Detail view for schedules"""
    model = Schedule
    template_name = 'schedules/detail.html'
    context_object_name = 'schedule'
    
    def get_queryset(self):
        queryset = Schedule.objects.select_related('employee', 'client', 'approved_by')
        
        if self.request.user.is_employee:
            queryset = queryset.filter(employee=self.request.user)
        elif self.request.user.is_client:
            queryset = queryset.filter(client__name=self.request.user.get_full_name())
        # Supervisors see all schedules
        
        return queryset


class ScheduleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update view for schedules"""
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/update.html'
    success_url = reverse_lazy('schedules:list')
    
    def test_func(self):
        schedule = self.get_object()
        # Employees can edit their own drafts, supervisors can edit any
        return (self.request.user.is_employee and schedule.employee == self.request.user and schedule.status == 'draft') or self.request.user.is_supervisor
    
    def form_valid(self, form):
        messages.success(self.request, 'Schedule updated successfully!')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ScheduleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete view for schedules"""
    model = Schedule
    template_name = 'schedules/delete.html'
    success_url = reverse_lazy('schedules:list')
    
    def test_func(self):
        schedule = self.get_object()
        # Employees can delete their own drafts, supervisors can delete any
        return (self.request.user.is_employee and schedule.employee == self.request.user and schedule.status == 'draft') or self.request.user.is_supervisor
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Schedule deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ScheduleSubmitView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Submit schedule for approval"""
    template_name = 'schedules/submit.html'
    
    def test_func(self):
        schedule = get_object_or_404(Schedule, pk=self.kwargs['pk'])
        return self.request.user.is_employee and schedule.employee == self.request.user and schedule.status == 'draft'
    
    def post(self, request, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=kwargs['pk'])
        schedule.submit_for_approval()
        messages.success(request, 'Schedule submitted for approval!')
        return redirect('schedules:detail', pk=schedule.pk)


class ScheduleApproveView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Approve schedule (supervisors only)"""
    template_name = 'schedules/approve.html'
    
    def test_func(self):
        return self.request.user.is_supervisor
    
    def post(self, request, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=kwargs['pk'])
        schedule.approve(request.user)
        messages.success(request, 'Schedule approved successfully!')
        return redirect('schedules:approvals')


class ScheduleRejectView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Reject schedule (supervisors only)"""
    template_name = 'schedules/reject.html'
    
    def test_func(self):
        return self.request.user.is_supervisor
    
    def post(self, request, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=kwargs['pk'])
        reason = request.POST.get('reason', '')
        schedule.reject(request.user, reason)
        messages.success(request, 'Schedule rejected.')
        return redirect('schedules:approvals')


class ScheduleCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view for schedules"""
    template_name = 'schedules/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current month or specified month
        year = int(self.request.GET.get('year', timezone.now().year))
        month = int(self.request.GET.get('month', timezone.now().month))
        
        context['current_year'] = year
        context['current_month'] = month
        context['month_name'] = datetime(year, month, 1).strftime('%B %Y')
        
        # Get schedules for the month
        month_start = datetime(year, month, 1).date()
        month_end = datetime(year, month, monthrange(year, month)[1]).date()
        
        schedules = Schedule.objects.filter(
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('employee', 'client')
        
        if self.request.user.is_employee:
            schedules = schedules.filter(employee=self.request.user)
        elif self.request.user.is_client:
            schedules = schedules.filter(client__name=self.request.user.get_full_name())
        
        # Generate calendar days
        calendar_days = self._generate_calendar_days(year, month, schedules)
        context['calendar_days'] = calendar_days
        
        return context
    
    def _generate_calendar_days(self, year, month, schedules):
        """Generate calendar days with schedules"""
        import calendar
        from datetime import date
        
        # Get the first day of the month and how many days it has
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Get the weekday of the first day (0 = Sunday, 6 = Saturday)
        # Convert from weekday() (0=Monday) to isoweekday() (1=Monday) then adjust for Sunday start
        first_weekday = (first_day.weekday() + 1) % 7  # Convert to Sunday=0 format
        
        # Create a list to hold all calendar days
        calendar_days = []
        
        # Add empty days for the previous month
        for i in range(first_weekday):
            calendar_days.append({
                'day': '',
                'is_today': False,
                'is_other_month': True,
                'schedules': []
            })
        
        # Add days for the current month
        today = timezone.now().date()
        for day in range(1, last_day.day + 1):
            current_date = date(year, month, day)
            day_schedules = [s for s in schedules if s.start_date == current_date]
            
            calendar_days.append({
                'day': day,
                'is_today': current_date == today,
                'is_other_month': False,
                'schedules': day_schedules
            })
        
        # Add empty days for the next month to complete the grid
        remaining_days = 42 - len(calendar_days)  # 6 weeks * 7 days
        for i in range(remaining_days):
            calendar_days.append({
                'day': '',
                'is_today': False,
                'is_other_month': True,
                'schedules': []
            })
        
        return calendar_days


class ScheduleTableView(LoginRequiredMixin, TemplateView):
    """Table view for schedules"""
    template_name = 'schedules/table.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get schedules with filtering
        schedules = Schedule.objects.select_related('employee', 'client', 'approved_by')
        
        if self.request.user.is_employee:
            schedules = schedules.filter(employee=self.request.user)
        elif self.request.user.is_client:
            schedules = schedules.filter(client__name=self.request.user.get_full_name())
        
        # Apply filters
        status_filter = self.request.GET.get('status')
        if status_filter:
            schedules = schedules.filter(status=status_filter)
        
        client_filter = self.request.GET.get('client')
        if client_filter:
            schedules = schedules.filter(client_id=client_filter)
        
        context['schedules'] = schedules.order_by('-created_at')
        context['clients'] = Client.objects.filter(is_active=True)
        context['status_choices'] = Schedule.STATUS_CHOICES
        
        return context


class ScheduleApprovalsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Approvals view for supervisors"""
    template_name = 'schedules/approvals.html'
    
    def test_func(self):
        return self.request.user.is_supervisor
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending schedules
        pending_schedules = Schedule.objects.filter(
            status='submitted'
        ).select_related('employee', 'client').order_by('-submitted_at')
        
        context['pending_schedules'] = pending_schedules
        
        return context


class CalendarMonthView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint for calendar month data"""
    template_name = 'schedules/calendar_month.html'
    
    def get_template_names(self):
        """Return appropriate template based on request type"""
        if self.request.headers.get('HX-Request'):
            return ['schedules/calendar_grid.html']
        return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = kwargs['year']
        month = kwargs['month']
        
        context['current_year'] = year
        context['current_month'] = month
        context['month_name'] = datetime(year, month, 1).strftime('%B %Y')
        
        # Get schedules for the month
        month_start = datetime(year, month, 1).date()
        month_end = datetime(year, month, monthrange(year, month)[1]).date()
        
        schedules = Schedule.objects.filter(
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('employee', 'client')
        
        if self.request.user.is_employee:
            schedules = schedules.filter(employee=self.request.user)
        elif self.request.user.is_client:
            schedules = schedules.filter(client__name=self.request.user.get_full_name())
        
        context['schedules'] = schedules
        
        # Generate calendar days
        context['calendar_days'] = self._generate_calendar_days(year, month, schedules)
        
        return context
    
    def _generate_calendar_days(self, year, month, schedules):
        """Generate calendar days for the month view"""
        from calendar import monthrange, weekday
        from datetime import date, datetime
        
        # Get the first day of the month and how many days it has
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        # Get the first day of the week (0 = Monday, 6 = Sunday)
        # We want Sunday to be the first day, so we adjust
        first_weekday = (first_day.weekday() + 1) % 7  # Convert Monday=0 to Sunday=0
        
        # Create a list to hold all calendar days
        calendar_days = []
        
        # Add empty cells for days before the first day of the month
        for _ in range(first_weekday):
            calendar_days.append({'day': None, 'schedules': [], 'schedules_count': 0, 'is_today': False})
        
        # Add all days of the month
        today = date.today()
        for day in range(1, last_day.day + 1):
            current_date = date(year, month, day)
            day_schedules = [s for s in schedules if s.start_date == current_date]
            
            calendar_days.append({
                'day': day,
                'schedules': day_schedules,
                'schedules_count': len(day_schedules),
                'is_today': current_date == today
            })
        
        # Fill remaining cells to complete the grid (6 weeks = 42 days)
        while len(calendar_days) < 42:
            calendar_days.append({'day': None, 'schedules': [], 'schedules_count': 0, 'is_today': False})
        
        return calendar_days


class ScheduleTableDataView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint for table data"""
    template_name = 'schedules/table_data.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get schedules with filtering
        schedules = Schedule.objects.select_related('employee', 'client', 'approved_by')
        
        if self.request.user.is_employee:
            schedules = schedules.filter(employee=self.request.user)
        elif self.request.user.is_client:
            schedules = schedules.filter(client__name=self.request.user.get_full_name())
        
        # Apply filters
        status_filter = self.request.GET.get('status')
        if status_filter:
            schedules = schedules.filter(status=status_filter)
        
        client_filter = self.request.GET.get('client')
        if client_filter:
            schedules = schedules.filter(client_id=client_filter)
        
        context['schedules'] = schedules.order_by('-created_at')
        
        return context