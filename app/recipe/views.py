"""Views for recipe APIs."""
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers






# """
# Use case:
# This schema extension decorator documents the query parameters available for filtering recipes.
# It enables API consumers to:
# 1. Filter recipes by one or more tag IDs (e.g. ?tags=1,2,3)
# 2. Filter recipes by one or more ingredient IDs (e.g. ?ingredients=1,2,3) 
# 3. Combine both filters (e.g. ?tags=1&ingredients=2)

# The schema:
# - Defines two query parameters: 'tags' and 'ingredients'
# - Specifies that both accept comma-separated strings of IDs
# - Provides descriptions explaining the purpose of each parameter
# - Integrates with OpenAPI/Swagger documentation
# """


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter'
            )
        ]
    )
)


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


    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers."""
        if not qs:
            return []
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Filter and return recipes based on query parameters.
        
        Use case:
        When users want to filter recipes by tags and/or ingredients, they can provide
        query parameters in the URL. For example:
        - /api/recipes/?tags=1,2 returns recipes with tag IDs 1 OR 2
        - /api/recipes/?ingredients=1,2 returns recipes with ingredient IDs 1 OR 2
        - /api/recipes/?tags=1&ingredients=2 returns recipes with tag ID 1 AND ingredient ID 2
        
        The method:
        1. Extracts tag and ingredient IDs from query parameters
        2. Filters recipes that match ANY of the specified tags
        3. Filters recipes that match ANY of the specified ingredients
        4. Returns only recipes belonging to the authenticated user
        5. Orders results by ID and removes duplicates
        """
        # Get tag and ingredient IDs from query parameters
        tags = self._params_to_ints(self.request.query_params.get('tags'))
        ingredients = self._params_to_ints(self.request.query_params.get('ingredients'))
        
        # Start with base queryset
        queryset = self.queryset
        
        # Filter by tags if provided
        if tags:
            queryset = queryset.filter(tags__id__in=tags)
            
        # Filter by ingredients if provided    
        if ingredients:
            queryset = queryset.filter(ingredients__id__in=ingredients)
            
        # Return filtered queryset for authenticated user only
        return queryset.filter(user=self.request.user).order_by('-id').distinct()
    
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



@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,
                description='Filter by items assigned to recipes'   
            )
        ]
    )
)

class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags/ingredients for authenticated user.
        
        Use case:
        When users want to filter tags/ingredients by those assigned to recipes,
        they can provide the assigned_only parameter. For example:
        - /api/tags/?assigned_only=1 returns only tags that are used in recipes
        - /api/ingredients/?assigned_only=1 returns only ingredients that are used in recipes
        
        The method:
        1. Filters by authenticated user
        2. If assigned_only=1, filters to only tags/ingredients assigned to recipes
        3. Orders by name and removes duplicates
        """
        # Start with base queryset filtered by user
        queryset = self.queryset.filter(user=self.request.user)
        
        # Check if assigned_only parameter is provided
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        
        # If assigned_only is True, filter to only tags/ingredients assigned to recipes
        if assigned_only:
            # For tags, filter to those that are used in recipes
            if self.queryset.model == Tag:
                queryset = queryset.filter(recipe__isnull=False)
            # For ingredients, filter to those that are used in recipes
            elif self.queryset.model == Ingredient:
                queryset = queryset.filter(recipe__isnull=False)
        
        # Return ordered and distinct queryset
        return queryset.order_by('-name').distinct()



class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()





class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
   