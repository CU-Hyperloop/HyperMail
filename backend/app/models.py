from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

#  Stores company information with a constraint that either email or website must exist
class Company(models.Model):
    COMPANY_TYPES = [
        ('monetary', 'Monetary'),
        ('parts', 'Parts'),
    ]
    
    name = models.TextField(null=False, blank=False)  # Required field
    website = models.TextField(blank=True, null=True)
    email = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Add this field
    contact_person = models.TextField(blank=True, null=True)
    industry = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    size = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=COMPANY_TYPES)
    
    def clean(self):
        """
        Validate that either email or website is provided.
        """
        if not self.email and not self.website:
            raise ValidationError(
                "Either email or website must be provided."
            )
        
        super().clean()
    
    def save(self, *args, **kwargs):
        """
        Override save method to ensure validation runs before saving
        and prevent saving if neither email nor website exists.
        """
        self.full_clean()
        
        # Extra check - don't add to database if neither email nor website exists
        if not self.email and not self.website:
            return None  # Don't save
            
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"

#  Stores email templates that can be reused across emails
class Template(models.Model):
    TEMPLATE_TYPES = [
        ('monetary', 'Monetary'),
        ('parts', 'Parts'),
    ]
    
    subject = models.TextField()
    body = models.TextField()
    type = models.CharField(max_length=10, choices=TEMPLATE_TYPES)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.subject[:30]} ({self.type})"

# Stores emails sent to companies.
class Email(models.Model):
    STATUS_CHOICES = [
        ('responded', 'Responded'),
        ('not_responded', 'Not Responded'),
    ]
    
    EMAIL_TYPES = [
        ('monetary', 'Monetary'),
        ('parts', 'Parts'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='emails')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='emails')
    sent_at = models.DateTimeField(default=timezone.now)
    subject = models.TextField()
    body = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_responded')
    type = models.CharField(max_length=10, choices=EMAIL_TYPES)
    
    def __str__(self):
        return f"Email to {self.company}: {self.subject[:30]}"

# Stores user-entered prompts with associated links
class Prompt(models.Model):
    PROMPT_TYPES = [
        ('monetary', 'Monetary'),
        ('parts', 'Parts'),
    ]
    
    text = models.TextField()
    type = models.CharField(max_length=10, choices=PROMPT_TYPES)
    link = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.text[:50]} ({self.type})"