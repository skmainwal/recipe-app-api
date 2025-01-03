"""Views for recipe APIs."""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
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
    serializer_class = serializers.RecipeSerializer
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
    