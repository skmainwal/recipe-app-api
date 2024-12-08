"""
Database models.
"""
from django.db import models  # Importing Django's models module to define database models
from django.contrib.auth.models import (
    AbstractBaseUser,  # Base class for creating a custom user model
    BaseUserManager,   # Base class for creating a custom user manager
    PermissionsMixin,   # Mixin that adds permission-related fields and methods
)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        # Create a new user instance with the provided email and extra fields
        user = self.model(email=email, **extra_fields)
        # Set the user's password using Django's built-in method
        user.set_password(password)
        # Save the user instance to the database
        user.save(using=self._db)
        return user  # Return the created user instance


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    # Email field for the user, must be unique and has a max length of 255 characters
    email = models.EmailField(max_length=255, unique=True)
    # Name field for the user, with a max length of 255 characters
    name = models.CharField(max_length=255)
    # Boolean field indicating if the user is active
    is_active = models.BooleanField(default=True)
    # Boolean field indicating if the user has staff privileges
    is_staff = models.BooleanField(default=False)

    # Assign the custom user manager to the User model
    objects = UserManager()

    # Specify that the email field will be used as the unique identifier for authentication
    USERNAME_FIELD = 'email'