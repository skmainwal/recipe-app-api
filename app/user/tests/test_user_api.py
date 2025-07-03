"""
Test suite for the User API endpoints.

This module contains comprehensive tests for the user management API, covering:
1. User registration (public endpoint)
2. Token-based authentication (public endpoint) 
3. User profile management (authenticated endpoints)

The tests are organized into two main classes:
- PublicUserApiTests: Tests for endpoints that don't require authentication
- PrivateUserApiTests: Tests for endpoints that require user authentication

Use Cases Covered:
- User registration with validation
- Authentication token generation
- Profile retrieval and updates
- Error handling for invalid requests
- Security validation (password requirements, duplicate emails)
"""

# Django Testing Framework
# Use Case: Provides the base TestCase class for writing unit tests
# - TestCase handles database setup/teardown for each test
# - Provides assertion methods for validating test results
# - Manages test isolation (each test runs in its own transaction)
from django.test import TestCase

# Django Authentication System
# Use Case: Access to the User model for creating and managing test users
# - get_user_model() returns the active User model (custom or default)
# - Allows creating users with proper password hashing
# - Provides access to user authentication methods
from django.contrib.auth import get_user_model

# Django REST Framework Testing
# Use Case: Provides tools for testing REST API endpoints
# - APIClient simulates HTTP requests to API endpoints
# - Supports all HTTP methods (GET, POST, PUT, PATCH, DELETE)
# - Handles authentication, headers, and request/response formatting
from rest_framework.test import APIClient

# Django URL Resolution
# Use Case: Generate URLs for API endpoints during testing
# - reverse() converts URL names to actual URL paths
# - Ensures tests use the same URLs as the actual application
# - Makes tests more maintainable when URLs change
from django.urls import reverse

# Django REST Framework Status Codes
# Use Case: Provides HTTP status code constants for assertions
# - Makes test assertions more readable and maintainable
# - Ensures consistent status code checking across tests
# - Examples: status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST
from rest_framework import status


# URL constants for the user API endpoints
CREATE_USER_URL = reverse('user:create')  # POST /api/user/create/ - User registration endpoint
TOKEN_URL = reverse('user:token')  # POST /api/user/token/ - Authentication token generation endpoint
ME_URL = reverse('user:me')  # GET/PATCH /api/user/me/ - User profile management endpoint


def create_user(**params):
    """
    Helper function to create a test user.
    
    Args:
        **params: User parameters (email, password, name)
    
    Returns:
        User: Created user instance
        
    Use Case: Used throughout tests to create test users for authentication
    and data setup purposes.
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test suite for public user API endpoints (no authentication required).
    
    These tests cover user registration and authentication functionality
    that should be accessible to all users without requiring login.
    
    Use Cases:
    - New user registration
    - User authentication via token generation
    - Input validation and error handling
    - Security checks (password strength, duplicate emails)
    """

    def setUp(self):
        """
        Set up test environment before each test method.
        
        Creates a fresh API client for making HTTP requests to the user API.
        This ensures each test starts with a clean state.
        """
        self.client = APIClient()  # Initialize the API client for making requests

    def test_create_user_success(self):
        """
        Test successful user registration.
        
        Use Case: A new user wants to create an account with valid credentials.
        
        Test Scenario:
        1. Send POST request with valid user data (email, password, name)
        2. Verify user is created in database
        3. Verify password is properly hashed
        4. Verify sensitive data (password) is not returned in response
        5. Verify HTTP 201 Created status is returned
        
        Expected Behavior:
        - User account is successfully created
        - Password is securely hashed and stored
        - Response contains user data but not password
        """
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
        """
        Test duplicate email validation during user registration.
        
        Use Case: A user tries to register with an email that already exists.
        
        Test Scenario:
        1. Create a user with a specific email
        2. Attempt to create another user with the same email
        3. Verify the second request fails with appropriate error
        
        Expected Behavior:
        - First user creation succeeds
        - Second user creation fails with HTTP 400 Bad Request
        - Database maintains only one user with that email
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        create_user(**payload)  # Create a user with the given email
        res = self.client.post(CREATE_USER_URL, payload)  # Attempt to create another user with the same email

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check for bad request error

    def test_password_too_short_error(self):
        """
        Test password strength validation during user registration.
        
        Use Case: A user tries to register with a password that's too short.
        
        Test Scenario:
        1. Attempt to create user with password less than minimum length
        2. Verify request fails with validation error
        3. Verify no user is created in database
        
        Expected Behavior:
        - Request fails with HTTP 400 Bad Request
        - No user record is created in database
        - Appropriate validation error message is returned
        """
        payload = {
            'email': 'test@example.com',
            'password': 'pw',  # Password is too short (less than 5 characters)
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
        """
        Test successful authentication token generation.
        
        Use Case: A registered user wants to log in and get an authentication token.
        
        Test Scenario:
        1. Create a user with known credentials
        2. Send authentication request with valid email/password
        3. Verify token is generated and returned
        
        Expected Behavior:
        - Token is successfully generated
        - Response contains the authentication token
        - HTTP 200 OK status is returned
        """
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
        """
        Test authentication failure with invalid credentials.
        
        Use Case: A user attempts to log in with incorrect password.
        
        Test Scenario:
        1. Create a user with known credentials
        2. Attempt authentication with wrong password
        3. Verify authentication fails
        
        Expected Behavior:
        - Authentication fails with HTTP 400 Bad Request
        - No token is returned in response
        - Appropriate error message is provided
        """
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_create_token_blank_password(self):
        """
        Test authentication failure with blank password.
        
        Use Case: A user attempts to log in with an empty password field.
        
        Test Scenario:
        1. Send authentication request with empty password
        2. Verify request fails with validation error
        
        Expected Behavior:
        - Request fails with HTTP 400 Bad Request
        - No token is returned
        - Validation error is provided for empty password
        """
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
        Test that user profile endpoint requires authentication.
        
        Use Case: An unauthenticated user tries to access their profile.
        
        Test Scenario:
        1. Send GET request to profile endpoint without authentication
        2. Verify access is denied
        
        Expected Behavior:
        - Request fails with HTTP 401 Unauthorized
        - No user data is returned
        - Clear indication that authentication is required
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test suite for authenticated user API endpoints.
    
    These tests cover functionality that requires user authentication,
    such as profile management and user-specific operations.
    
    Use Cases:
    - Authenticated user profile retrieval
    - Profile information updates
    - Method validation for protected endpoints
    - Secure data access for logged-in users
    """

    def setUp(self):
        """
        Set up authenticated test environment before each test method.
        
        Creates a test user and authenticates the API client for all requests.
        This simulates a logged-in user session for testing protected endpoints.
        
        Setup Process:
        1. Creates a test user with known credentials
        2. Initializes API client
        3. Forces authentication for all subsequent requests
        """
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()  # Create a test client for making HTTP requests
        self.client.force_authenticate(user=self.user)  # Authenticate all requests with our test user

    def test_retrieve_profile_success(self):
        """
        Test successful profile retrieval for authenticated user.
        
        Use Case: A logged-in user wants to view their profile information.
        
        Test Scenario:
        1. Send GET request to profile endpoint with authentication
        2. Verify user's profile data is returned correctly
        3. Ensure only safe fields are exposed
        
        Expected Behavior:
        - HTTP 200 OK status is returned
        - Response contains user's name and email
        - Sensitive data (password, internal fields) is not exposed
        - Data matches the authenticated user's information
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """
        Test that POST method is not allowed on profile endpoint.
        
        Use Case: A user attempts to use POST method on profile endpoint.
        
        Test Scenario:
        1. Send POST request to profile endpoint
        2. Verify method is not allowed
        
        Expected Behavior:
        - Request fails with HTTP 405 Method Not Allowed
        - Clear indication that POST is not supported
        - Only GET and PATCH methods should be allowed
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)   

    def test_update_user_profile(self):
        """
        Test successful profile update for authenticated user.
        
        Use Case: A logged-in user wants to update their profile information.
        
        Test Scenario:
        1. Send PATCH request with updated user data
        2. Verify changes are saved to database
        3. Verify password is properly hashed when updated
        4. Confirm successful response
        
        Expected Behavior:
        - Profile updates are successfully saved
        - Password is properly hashed and stored securely
        - HTTP 200 OK status is returned
        - Updated data is reflected in database
        """
        payload = {'name': 'Updated Name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # Refresh user instance from database to get updated values
        self.assertEqual(self.user.name, payload['name'])  # Verify name was updated
        self.assertTrue(self.user.check_password(payload['password']))  # Verify password was updated and hashed
        self.assertEqual(res.status_code, status.HTTP_200_OK)









