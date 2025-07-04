"""Views for recipe APIs."""

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user) 

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name').distinct()
    


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()





class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
   