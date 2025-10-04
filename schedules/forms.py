from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Schedule
from clients.models import Client


class ScheduleForm(forms.ModelForm):
    """Form for creating and updating schedules"""
    
    class Meta:
        model = Schedule
        fields = ['client', 'start_date', 'start_time', 'end_date', 'end_time', 'status', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'start_date': forms.DateInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'time'}),
            'end_date': forms.DateInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'date'}),
            'end_time': forms.TimeInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter clients based on user role
        if user and user.is_employee:
            self.fields['client'].queryset = Client.objects.filter(is_active=True)
        elif user and user.is_supervisor:
            self.fields['client'].queryset = Client.objects.filter(is_active=True)
        else:
            self.fields['client'].queryset = Client.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')
        
        # Validate date logic
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before or equal to end date.")
        
        # Validate time logic
        if start_time and end_time and start_date == end_date:
            if start_time >= end_time:
                raise ValidationError("Start time must be before end time.")
        
        # Validate future dates only
        if start_date and start_date < timezone.now().date():
            raise ValidationError("Schedules can only be created for future dates.")
        
        # Validate duration (minimum 1 hour, maximum 12 hours)
        if start_date and end_date and start_time and end_time:
            from datetime import datetime, timedelta
            
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            duration = end_datetime - start_datetime
            
            if duration.total_seconds() < 3600:  # 1 hour
                raise ValidationError("Schedule duration must be at least 1 hour.")
            
            if duration.total_seconds() > 43200:  # 12 hours
                raise ValidationError("Schedule duration cannot exceed 12 hours.")
        
        return cleaned_data


class ScheduleApprovalForm(forms.Form):
    """Form for schedule approval actions"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('modify', 'Request Modification'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300'})
    )
    
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 3, 'placeholder': 'Optional reason or comments...'})
    )
    
    def clean_reason(self):
        action = self.cleaned_data.get('action')
        reason = self.cleaned_data.get('reason')
        
        if action in ['reject', 'modify'] and not reason:
            raise ValidationError("Reason is required for rejection or modification requests.")
        
        return reason
