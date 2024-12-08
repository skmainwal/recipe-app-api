from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


CREATE_USER_URL = reverse('user:create')  # URL for the user creation endpoint


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)  # Helper function to create a user


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        """Set up the test client for API requests."""
        self.client = APIClient()  # Initialize the API client for making requests

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)  # Send POST request to create user

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Check if user creation was successful
        user = get_user_model().objects.get(email=payload['email'])  # Retrieve the created user
        self.assertTrue(user.check_password(payload['password']))  # Verify the password is correct
        self.assertNotIn('password', res.data)  # Ensure password is not returned in the response

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        create_user(**payload)  # Create a user with the given email
        res = self.client.post(CREATE_USER_URL, payload)  # Attempt to create another user with the same email

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check for bad request error

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',  # Password is too short
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)  # Attempt to create user with short password

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check for bad request error
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # Check if user was created
        # Ensure user was not created
        self.assertFalse(user_exists)
