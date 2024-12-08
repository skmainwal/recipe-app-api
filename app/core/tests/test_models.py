"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        # Define the email and password for the test user
        email = 'test@example.com'
        password = 'testpass123'
        
        # Create a new user using the custom user model
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        
        # Assert that the user's email is set correctly
        self.assertEqual(user.email, email)
        
        # Assert that the user's password is set correctly and can be verified
        self.assertTrue(user.check_password(password))
