"""
Database models.
"""
import uuid
import os

# Importing Django's models module to define database models
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,  # Base class for creating a custom user model
    BaseUserManager,   # Base class for creating a custom user manager
    PermissionsMixin,  # Mixin that adds permission-related fields and methods
)

from django.conf import settings

def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image.
    
    This function generates a unique file path for storing recipe images.
    When a user uploads an image for a recipe, this function:
    1. Extracts the file extension from the original filename
    2. Generates a new unique filename using UUID to prevent naming conflicts
    3. Returns a path like 'uploads/recipe/uuid.jpg' where the image will be stored
    
    The generated path is used by Django to store the image in MEDIA_ROOT
    as configured in settings.py.
    """
    ext = os.path.splitext(filename)[1]  # Get file extension (e.g. .jpg)
    filename = f'{uuid.uuid4()}{ext}'    # Generate unique filename with UUID
    return os.path.join('uploads', 'recipe', filename)





class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError(
                'User must have an email address.'
            )  # Raise an error if email is not provided
        # Normalize the email address by lowercasing the domain part of it
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        # Set the user's password using Django's built-in method
        user.set_password(password)
        # Save the user instance to the database using the specified database alias
        user.save(using=self._db)
        return user  # Return the created user instance

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


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


class Recipe(models.Model):
    """Recipe object - represents a cooking recipe in the system."""
    # Link recipe to a specific user (foreign key relationship)
    # If user is deleted, all their recipes will be deleted (CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # Title of the recipe, required field with max length of 255 chars
    title = models.CharField(max_length=255)
    # Time to prepare/cook the recipe in minutes (integer field)
    time_minutes = models.IntegerField()
    # Price of the recipe - allows decimal numbers up to 999.99
    # max_digits=5 means total length, decimal_places=2 means 2 decimal points
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # Optional text field for recipe description/steps
    # blank=True means this field is optional
    description = models.TextField(blank=True)
    # Optional URL field to link to external recipe sources
    # blank=True means this field is optional
    link = models.CharField(max_length=255, blank=True)
    # Many-to-many relationship with tags
    # If a tag is deleted, it will not affect the recipe (PROTECT)
    tags = models.ManyToManyField('Tag', blank=True)
    # Many-to-many relationship with ingredients
    # If an ingredient is deleted, it will not affect the recipe (PROTECT)
    ingredients = models.ManyToManyField('Ingredient', blank=True)

    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        """Return string representation of recipe."""
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""
    # Link tag to a specific user (foreign key relationship)
    # If user is deleted, all their tags will be deleted (CASCADE)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return string representation of tag."""
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )    

    def __str__(self):
        """Return string representation of ingredient."""
        return self.name



