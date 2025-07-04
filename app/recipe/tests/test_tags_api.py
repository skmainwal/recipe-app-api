""" Test for the tags API."""

from decimal import Decimal

# Import Django's user model manager to create test users
from django.contrib.auth import get_user_model
# Import reverse to generate URLs from URL names
from django.urls import reverse
# Import TestCase for creating test classes
from django.test import TestCase

# Import HTTP status codes for assertions
from rest_framework import status
# Import APIClient for making HTTP requests in tests
from rest_framework.test import APIClient

# Import the Tag model from core app
from core.models import Recipe, Tag

# Import the TagSerializer for serializing tag data
from recipe.serializers import TagSerializer

# Import Decimal for handling price fields in recipes
from decimal import Decimal

# Generate the URL for the tag list endpoint using reverse lookup
# This creates the URL pattern for listing tags (e.g., /api/recipe/tags/)
TAGS_URL = reverse('recipe:tag-list')

# Generate the URL for the recipe list endpoint using reverse lookup
# This creates the URL pattern for creating/listing recipes (e.g., /api/recipe/recipes/)
RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    # Use Django's get_user_model() to get the active user model
    # This ensures compatibility with custom user models
    return get_user_model().objects.create_user(email, password)

class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        # Initialize API client for making HTTP requests in tests
        # This client simulates a web browser making requests
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        # Make a GET request to the tags endpoint without authentication
        # This simulates an unauthenticated user trying to access tags
        res = self.client.get(TAGS_URL)

        # Assert that the response status is 401 Unauthorized
        # This ensures the API properly rejects unauthenticated requests
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED) 

class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        # Initialize API client for making HTTP requests
        self.client = APIClient()
        # Create a test user for authentication
        self.user = create_user()
        # Force authenticate the client with the test user
        # This simulates a logged-in user making requests
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags.
        
        This test verifies that authenticated users can retrieve their own tags.
        
        Use Case:
        - User wants to see all their tags (e.g., for a tag selection dropdown)
        - The API should return all tags belonging to the authenticated user
        - Tags should be ordered by name for consistent display
        
        Steps:
        1. Create test tags for the authenticated user
        2. Make GET request to retrieve tags
        3. Verify the response matches the expected serialized data
        """
        # Create test tag data in the database
        # These tags belong to the authenticated user
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Make a GET request to retrieve all tags
        # Since user is authenticated, this should return their tags
        res = self.client.get(TAGS_URL)

        # Query all tags from database ordered by name (descending)
        # This represents what the API should return
        tags = Tag.objects.all().order_by('-name')
        # Serialize the tags using the TagSerializer
        # This converts the queryset to JSON format
        serializer = TagSerializer(tags, many=True)

        # Assert that the API returns a successful response (200 OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the API response matches the serialized data
        # This ensures the API returns the correct data format
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user.
        
        This test verifies data isolation - users can only see their own tags.
        
        Use Case:
        - Multiple users in the system should have their own private tags
        - User A should not see User B's tags and vice versa
        - This ensures privacy and data security in a multi-user system
        
        Steps:
        1. Create a second user with their own tags
        2. Create a tag for the authenticated user
        3. Make GET request to retrieve tags
        4. Verify only the authenticated user's tags are returned
        """
        # Create a second user to test data isolation
        # This ensures users can't see each other's tags
        user2 = create_user(email='user2@example.com')
        # Create a tag belonging to the second user
        # This tag should NOT appear in the first user's response
        Tag.objects.create(user=user2, name='Fruity')
        # Create a tag belonging to the authenticated user
        # This tag SHOULD appear in the response
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        # Make a GET request to retrieve tags
        # The API should only return tags belonging to the authenticated user
        res = self.client.get(TAGS_URL)

        # Assert that the API returns a successful response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that only one tag is returned (the user's own tag)
        # This verifies that data isolation is working correctly
        self.assertEqual(len(res.data), 1)
        # Assert that the returned tag is the one belonging to the authenticated user
        # This ensures the correct tag is returned
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_update_tag(self):
        """Test updating a tag.
        
        This test verifies that authenticated users can update their own tags.
        
        Use Case:
        - User wants to rename an existing tag (e.g., "After Dinner" to "Dessert")
        - The API should allow PATCH requests to update tag names
        - Only the tag owner should be able to update their tags
        
        Steps:
        1. Create a tag for the authenticated user
        2. Prepare updated tag data
        3. Make PATCH request to update the tag
        4. Verify the tag was updated in the database
        """
        # Create a tag that belongs to the authenticated user
        # This simulates an existing tag that the user wants to update
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        # Prepare the updated tag data
        # This represents the new name the user wants to give the tag
        payload = {'name': 'Dessert'}
        # Generate the URL for updating this specific tag
        url = detail_url(tag.id)

        # Make PATCH request to update the tag
        # PATCH is used for partial updates (only the name field in this case)
        res = self.client.patch(url, payload)

        # Assert that the update was successful (200 OK)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Refresh the tag object from the database to get the updated data
        tag.refresh_from_db()
        # Verify that the tag name was actually updated in the database
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag.
        
        This test verifies that authenticated users can delete their own tags.
        
        Use Case:
        - User wants to remove a tag they no longer need
        - The API should allow DELETE requests to remove tags
        - Only the tag owner should be able to delete their tags
        - When a tag is deleted, it should be completely removed from the database
        
        Steps:
        1. Create a tag for the authenticated user
        2. Make DELETE request to remove the tag
        3. Verify the tag was deleted from the database
        """
        # Create a tag that belongs to the authenticated user
        # This simulates an existing tag that the user wants to delete
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        # Generate the URL for deleting this specific tag
        url = detail_url(tag.id)

        # Make DELETE request to remove the tag
        # This should completely remove the tag from the database
        res = self.client.delete(url)

        # Assert that the deletion was successful (204 No Content)
        # 204 is the appropriate status code for successful deletion with no response body
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Verify that no tags exist for this user after deletion
        # This ensures the tag was completely removed from the database
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_create_recipe_with_new_tag(self):
        """Test creating a recipe with a new tag.
        
        This test verifies that when creating a recipe with tags that don't exist yet,
        the system automatically creates the new tags and associates them with the recipe.
        
        Use Case:
        - User wants to create a recipe and add tags that haven't been created before
        - The API should automatically create these new tags and link them to the recipe
        - This provides a convenient way to add tags during recipe creation
        
        Steps:
        1. Prepare recipe data with new tag names
        2. Make POST request to create recipe with tags
        3. Verify recipe is created successfully
        4. Verify new tags are created and associated with the recipe
        5. Verify tags belong to the authenticated user
        """
        # Prepare recipe data with new tags that don't exist in the database
        # This simulates a user creating a recipe with tags they haven't used before
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],  # New tags to be created
        }
        
        # Make POST request to create recipe with new tags
        # The API should automatically create the tags and associate them with the recipe
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        # Assert that the recipe was created successfully (201 Created)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Verify that exactly one recipe was created for the authenticated user
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        
        # Get the created recipe to verify tag associations
        recipe = recipes[0]
        
        # Verify that exactly 2 tags were created and associated with the recipe
        # This ensures the API properly created the new tags
        self.assertEqual(recipe.tags.count(), 2)
        
        # Verify each tag from the payload was created and associated correctly
        for tag in payload['tags']:
            # Check if the tag exists in the database and is associated with the recipe
            # This verifies that the API created the tags with the correct names
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,  # Ensure tags belong to the authenticated user
            ).exists()
            self.assertTrue(exists)


    def test_filter_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes.
        
        Use case:
        When users want to see only tags that are actually being used in recipes,
        they can filter the tags list using the assigned_only parameter.
        This test verifies that:
        1. Only tags associated with recipes are returned when filtered
        2. Unused tags are excluded from results
        3. The filtering parameter works as expected
        """
        # Create two test tags - one to assign to a recipe, one unassigned
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        # Create a recipe and assign only the first tag to it
        recipe = Recipe.objects.create(
            title='Pancakes',
            time_minutes=10,
            price=Decimal('5.00'),  
            user=self.user
        )
        recipe.tags.add(tag1)

        # Make API request with assigned_only filter
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        # Serialize both tags for comparison
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        # Verify that only the assigned tag is in the response
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)


    def test_filter_tags_unique(self):
        """Test filtering tags returns a unique list.
        
        Use case:
        When filtering tags that are assigned to recipes, we want to ensure
        that tags are not duplicated in the results even if they are used
        in multiple recipes. This test verifies that:
        1. A tag used in multiple recipes appears only once in filtered results
        2. The assigned_only filter properly deduplicates tags
        3. The count of returned tags is correct
        """
        # Create test tags - one to assign to recipes, one unassigned
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')

        # Create first recipe and assign the tag
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=10,
            price=Decimal('5.00'),  
            user=self.user
        )
        recipe1.tags.add(tag)

        # Create second recipe and assign the same tag
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user
        )
        recipe2.tags.add(tag)

        # Filter tags by assigned_only and verify unique results
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)  # Should only return one tag
