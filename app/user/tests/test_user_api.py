from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


CREATE_USER_URL = reverse('user:create')  # URL for the user creation endpoint
TOKEN_URL = reverse('user:token')  # URL for the token generation endpoint
ME_URL = reverse('user:me')  # URL for the user profile endpoint


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

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)  # Create a user with the given details

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)  # Send POST request to generate token

        self.assertIn('token', res.data)  # Check if token is in the response data
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check if token generation was successful

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication.
    This test class focuses on endpoints that require a user to be logged in.
    It tests the authenticated user's ability to retrieve and update their profile."""

    def setUp(self):
        """Create test client and authenticate user.
        This method runs before each test:
        1. Creates a test user
        2. Creates an API client
        3. Forces authentication for all requests"""
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()  # Create a test client for making HTTP requests
        self.client.force_authenticate(user=self.user)  # Authenticate all requests with our test user

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user.
        Verifies that:
        1. The GET request to /api/user/me/ returns HTTP 200
        2. The response contains the correct user data
        3. Only safe fields (name, email) are returned"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint.
        Verifies that:
        1. POST requests to /api/user/me/ are not allowed
        2. Returns HTTP 405 Method Not Allowed"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)   

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user.
        Verifies that:
        1. User can update their name and password
        2. Changes are saved to the database
        3. Returns HTTP 200 on successful update
        4. Password is properly hashed when updated"""
        payload = {'name': 'Updated Name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # Refresh user instance from database to get updated values
        self.assertEqual(self.user.name, payload['name'])  # Verify name was updated
        self.assertTrue(self.user.check_password(payload['password']))  # Verify password was updated and hashed
        self.assertEqual(res.status_code, status.HTTP_200_OK)   









