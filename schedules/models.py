from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
from clients.models import Client


class Schedule(models.Model):
    """
    Schedule model for managing employee-client schedules
    Based on REQUIREMENTS.md section 2.1 Core Entities and 3.1 Schedule Creation
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),
    ]
    
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='schedules',
        limit_choices_to={'role': 'employee'},
        help_text="Employee who created the schedule"
    )
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text="Client for the schedule"
    )
    
    start_date = models.DateField(
        help_text="Start date of the schedule"
    )
    
    start_time = models.TimeField(
        help_text="Start time of the schedule"
    )
    
    end_date = models.DateField(
        help_text="End date of the schedule"
    )
    
    end_time = models.TimeField(
        help_text="End time of the schedule"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the schedule"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments"
    )
    
    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the schedule was submitted for approval"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_schedules',
        limit_choices_to={'role': 'supervisor'},
        help_text="Supervisor who approved the schedule"
    )
    
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the schedule was approved"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for rejection if applicable"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'start_date']),
            models.Index(fields=['client', 'start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.client.name} ({self.start_date})"
    
    def clean(self):
        """Validate schedule data based on business rules"""
        super().clean()
        
        # Validate date logic
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before or equal to end date.")
        
        # Validate time logic
        if self.start_time and self.end_time:
            if self.start_date == self.end_date and self.start_time >= self.end_time:
                raise ValidationError("Start time must be before end time.")
        
        # Validate future dates only
        if self.start_date and self.start_date < timezone.now().date():
            raise ValidationError("Schedules can only be created for future dates.")
        
        # Validate duration (minimum 1 hour, maximum 12 hours)
        if self.start_date and self.end_date and self.start_time and self.end_time:
            from datetime import datetime, timedelta
            
            start_datetime = datetime.combine(self.start_date, self.start_time)
            end_datetime = datetime.combine(self.end_date, self.end_time)
            duration = end_datetime - start_datetime
            
            if duration.total_seconds() < 3600:  # 1 hour
                raise ValidationError("Schedule duration must be at least 1 hour.")
            
            if duration.total_seconds() > 43200:  # 12 hours
                raise ValidationError("Schedule duration cannot exceed 12 hours.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duration_hours(self):
        """Calculate total duration in hours"""
        if self.start_date and self.end_date and self.start_time and self.end_time:
            from datetime import datetime
            start_datetime = datetime.combine(self.start_date, self.start_time)
            end_datetime = datetime.combine(self.end_date, self.end_time)
            duration = end_datetime - start_datetime
            return round(duration.total_seconds() / 3600, 2)
        return 0
    
    @property
    def is_pending_approval(self):
        """Check if schedule is pending approval"""
        return self.status == 'submitted'
    
    @property
    def is_approved(self):
        """Check if schedule is approved"""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Check if schedule is rejected"""
        return self.status == 'rejected'
    
    def submit_for_approval(self):
        """Submit schedule for supervisor approval"""
        if self.status == 'draft':
            self.status = 'submitted'
            self.submitted_at = timezone.now()
            self.save(update_fields=['status', 'submitted_at'])
    
    def approve(self, supervisor):
        """Approve schedule by supervisor"""
        if self.status == 'submitted' and supervisor.is_supervisor:
            self.status = 'approved'
            self.approved_by = supervisor
            self.approved_at = timezone.now()
            self.save(update_fields=['status', 'approved_by', 'approved_at'])
    
    def reject(self, supervisor, reason=None):
        """Reject schedule by supervisor"""
        if self.status == 'submitted' and supervisor.is_supervisor:
            self.status = 'rejected'
            self.approved_by = supervisor
            self.approved_at = timezone.now()
            self.rejection_reason = reason
            self.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason'])
    
    def request_modification(self, supervisor, reason=None):
        """Request modification by supervisor"""
        if self.status == 'submitted' and supervisor.is_supervisor:
            self.status = 'modified'
            self.approved_by = supervisor
            self.approved_at = timezone.now()
            self.rejection_reason = reason
            self.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason'])


class ScheduleConflict(models.Model):
    """
    Model to track schedule conflicts
    """
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='conflicts'
    )
    
    conflicting_schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='conflicted_by'
    )
    
    conflict_type = models.CharField(
        max_length=50,
        choices=[
            ('employee_overlap', 'Employee Time Overlap'),
            ('client_overlap', 'Client Time Overlap'),
            ('insufficient_gap', 'Insufficient Gap Between Schedules'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'schedule_conflicts'
        unique_together = ['schedule', 'conflicting_schedule']
    
    def __str__(self):
        return f"Conflict: {self.schedule} vs {self.conflicting_schedule}"