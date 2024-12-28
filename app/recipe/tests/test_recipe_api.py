"""Test for recipe APIs."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer


# URL for accessing the recipe list endpoint
RECIPES_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return a sample recipe.
    
    Args:
        user: The user who owns the recipe
        **params: Optional parameters to override default recipe values
    
    Returns:
        Recipe object
    """
    # Default values for creating a recipe
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample recipe description.',
        'link': 'http://example.com/recipe.pdf',
    }

    # defaults.update(params) allows overriding default values with custom ones
    # Example 1: create_recipe(user, title="Pasta Carbonara")
    #   - results in: {'title': 'Pasta Carbonara', 'time_minutes': 22, ...}
    #
    # Example 2: create_recipe(user, title="Pizza", time_minutes=30, price=Decimal('15.00'))
    #   - results in: {'title': 'Pizza', 'time_minutes': 30, 'price': Decimal('15.00'), ...}
    #
    # Any keys in params will override the same keys in defaults, while
    # unspecified values remain as their defaults
    defaults.update(params)  # Merge provided params with defaults
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests.
    
    Tests behavior of the API when requests are made without authentication.
    """

    def setUp(self):
        """Create test client."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to access recipes.
        
        Verifies that unauthenticated requests return 401 Unauthorized.
        """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests.
    
    Tests behavior of the API when requests are made with valid authentication.
    """

    def setUp(self):
        """Create test client and authenticated user."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)  # Authenticate all requests
    
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes.
        
        Steps:
        1. Create two sample recipes
        2. Make GET request to recipe list endpoint
        3. Check response status is 200 OK
        4. Verify returned data matches the serialized recipes
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')  # Get recipes in reverse ID order
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Compare API response with serialized data


    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user.
        
        Steps:
        1. Create another user in the system
        2. Create a recipe owned by the other user
        3. Create a recipe owned by the authenticated user
        4. Make GET request to recipe list endpoint
        5. Verify only recipes for authenticated user are returned
        
        This test ensures that users can only view their own recipes
        and not recipes created by other users in the system.
        """
        # Create another user to test recipe isolation
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )   
        # Create recipe for other user - this should not be visible
        create_recipe(user=other_user)
        # Create recipe for authenticated user - this should be visible
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # Filter recipes to only include authenticated user's recipes
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Verify only authenticated user's recipes are returned

    
