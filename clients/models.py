from django.db import models
from django.core.validators import RegexValidator


class Client(models.Model):
    """
    Client model for managing client information
    Based on REQUIREMENTS.md section 2.1 Core Entities
    """
    name = models.CharField(
        max_length=255,
        help_text="Client company or organization name"
    )
    
    contact_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Primary contact email"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Primary contact phone number"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Client address"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the client is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def contact_info(self):
        """Return formatted contact information"""
        info = []
        if self.contact_email:
            info.append(f"Email: {self.contact_email}")
        if self.contact_phone:
            info.append(f"Phone: {self.contact_phone}")
        return " | ".join(info)