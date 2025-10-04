from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model with role-based access control
    Based on REQUIREMENTS.md section 1.1 User Roles and Permissions
    """
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('supervisor', 'Supervisor'),
        ('client', 'Client'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        help_text="User role determines access permissions"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Phone number with country code"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_employee(self):
        return self.role == 'employee'
    
    @property
    def is_supervisor(self):
        return self.role == 'supervisor'
    
    @property
    def is_client(self):
        return self.role == 'client'
    
    def get_role_display(self):
        return dict(self.ROLE_CHOICES)[self.role]
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username