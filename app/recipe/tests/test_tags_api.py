""" Test for the tags API."""

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
from core.models import Tag

# Import the TagSerializer for serializing tag data
from recipe.serializers import TagSerializer

# Generate the URL for the tag list endpoint using reverse lookup
# This creates the URL pattern for listing tags (e.g., /api/recipe/tags/)
TAGS_URL = reverse('recipe:tag-list')

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
        """Test retrieving a list of tags."""
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
        """Test that tags returned are for the authenticated user."""
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
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

  
        