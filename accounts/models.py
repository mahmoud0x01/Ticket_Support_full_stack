from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User'),
        ('support', 'Support Staff'),
        ('admin', 'Administrator'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    age = models.PositiveIntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tickets_submitted = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"User Profile: {self.user.email}"


class SupportProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='support_profile')
    tickets_assigned = models.PositiveIntegerField(default=0)
    tickets_resolved = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Support Profile: {self.user.email}"
