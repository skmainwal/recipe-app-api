"""Views for recipe APIs."""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs.
    
    This viewset provides default implementations for common actions:
    - List recipes (GET)
    - Create recipe (POST)
    - Retrieve recipe (GET <id>)
    - Update recipe (PUT/PATCH <id>)
    - Delete recipe (DELETE <id>)
    """
    # Serializer class that handles converting Recipe objects to/from JSON
    serializer_class = serializers.RecipeDetailSerializer
    # Base queryset of all recipes in the database
    queryset = Recipe.objects.all()
    # Specifies that token authentication is required for all endpoints
    authentication_classes = [TokenAuthentication]
    # Ensures only authenticated users can access the endpoints
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user.
        
        Returns:
            Queryset of Recipe objects filtered by the authenticated user,
            ordered by ID in descending order (newest first).
            The distinct() call ensures no duplicate recipes are returned.
        """
        return self.queryset.filter(user=self.request.user).order_by('-id').distinct()
    
    def get_serializer_class(self):
        """Return the serializer class for request.
        
        Returns:
            Serializer class based on the action being performed.
        """
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user) 


class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name').distinct()
    
    def perform_create(self, serializer):
        """Create a new tag."""
        serializer.save(user=self.request.user)

