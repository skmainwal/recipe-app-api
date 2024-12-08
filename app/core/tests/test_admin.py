"""
Test for the Django admin modifications.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Test for Django admin."""

    def setUp(self):
        """Create user and client."""
        # Initialize the test client
        self.client = Client()
        # Create a superuser for testing admin functionalities
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com', password='testpass123')
        # Log in the superuser
        self.client.force_login(self.admin_user)
        # Create a regular user for testing user-related functionalities
        self.user = get_user_model().objects.create_user(
            email='user@example.com', password='testpass123', name='Test User')

    def test_users_list(self):
        """Test that users are listed on user page."""
        # Get the URL for the user list page in the admin
        url = reverse('admin:core_user_changelist')
        # Perform a GET request to the user list page
        res = self.client.get(url)

        # Check that the response contains the user's name and email
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        # Get the URL for the edit user page for the created user
        url = reverse('admin:core_user_change', args=[self.user.id])
        # Perform a GET request to the edit user page
        res = self.client.get(url)
        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        # Get the URL for the add user page in the admin
        url = reverse('admin:core_user_add')
        # Perform a GET request to the add user page
        res = self.client.get(url)
        # Check that the response status code is 200 (OK)
        self.assertEqual(res.status_code, 200)
