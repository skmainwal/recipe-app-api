"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from core import models

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        # Assert that the user is a superuser
        self.assertTrue(user.is_superuser)

        # Assert that the user is active
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        # Create a test user that will own the recipe
        # This is required because recipes must be associated with a user
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        # Create a new recipe instance with test data
        # - user: The owner of the recipe
        # - title: Name of the recipe
        # - time_minutes: How long it takes to prepare
        # - price: Cost of ingredients (using Decimal for precise currency handling)
        # - description: Brief overview of the recipe
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )

        # Test that the string representation of the recipe
        # matches the recipe's title, which is the expected behavior
        # This verifies that the __str__ method is implemented correctly
        self.assertEqual(str(recipe), recipe.title)


    def test_create_recipe_with_new_tag(self):
        """Test creating a recipe with a new tag."""
        # Create a test user that will own the recipe
        # This is required because recipes must be associated with a user
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')
        self.assertEqual(str(tag), tag.name)


    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1'
        )
        self.assertEqual(str(ingredient), ingredient.name)  



       

