from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError

class VoterIDRegistry(models.Model):
    """Registry of valid voter IDs that can be used for registration"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('used', 'Used'),
        ('blocked', 'Blocked'),
    ]
    
    voter_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    registered_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_voter_ids'
    )
    registered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Voter ID Registry'
        verbose_name_plural = 'Voter ID Registry'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.voter_id} - {self.status}"
    
    def mark_as_used(self, user):
        """Mark this voter ID as used by a user"""
        from django.utils import timezone
        self.status = 'used'
        self.registered_by = user
        self.registered_at = timezone.now()
        self.save()


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, voter_id, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not voter_id:
            raise ValueError('Users must have a voter ID')
        
        email = self.normalize_email(email)
        user = self.model(email=email, voter_id=voter_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, voter_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, voter_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email and voter_id authentication"""
    
    ROLE_CHOICES = [
        ('voter', 'Voter'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    email = models.EmailField(unique=True, max_length=255)
    voter_id = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='voter')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['voter_id', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.email} ({self.voter_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def is_voter(self):
        return self.role == 'voter'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_super_admin(self):
        return self.role == 'super_admin'