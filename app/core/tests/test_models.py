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

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        # Define a list of sample email addresses and their expected normalized forms
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        # Iterate over each sample email and its expected normalized form
        for email, expected in sample_emails:
            # Create a new user with the sample email
            user = get_user_model().objects.create_user(email, 'sample123')

            # Assert that the user's email is normalized as expected
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')
