"""
Test for the ingredients API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """Return ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])    


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a test user."""
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint."""
        res = self.client.get(INGREDIENT_URL)   

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Ingredient1')
        Ingredient.objects.create(user=self.user, name='Ingredient2')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')    
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())  


    def test_filter_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes.
        
        Use case:
        When users want to see only ingredients that are actually being used in recipes,
        they can filter the ingredients list using the assigned_only parameter.
        This test verifies that:
        1. Only ingredients associated with recipes are returned when filtered
        2. Unused ingredients are excluded from results
        3. The filtering parameter works as expected
        """
        # Create two test ingredients
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')

        # Create a recipe and assign only the first ingredient to it
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user
        )   
        recipe.ingredients.add(in1)

        # Make API request with assigned_only filter
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        # Serialize both ingredients for comparison
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        # Verify that only the assigned ingredient is in the response
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)


    def test_filter_ingredients_unique(self):
        """Test filtering ingredients returns a unique list.
        
        Use case:
        When filtering ingredients that are assigned to recipes, we want to ensure
        that ingredients are not duplicated in the results even if they are used
        in multiple recipes. This test verifies that:
        1. An ingredient used in multiple recipes appears only once in filtered results
        2. The assigned_only filter properly deduplicates ingredients
        3. The count of returned ingredients is correct
        """
        # Create test ingredients - one to assign to recipes, one unassigned
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')

        # Create first recipe and assign the ingredient
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user      
        )
        recipe1.ingredients.add(ingredient)

        # Create second recipe and assign the same ingredient
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        # Filter ingredients by assigned_only and verify unique results
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)  # Should only return one ingredient



    