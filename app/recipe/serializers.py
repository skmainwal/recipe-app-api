"""Serializers for recipe API."""

from rest_framework import serializers

from core.models import Recipe, Tag



class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes.
    
    This serializer converts Recipe model instances to/from JSON format.
    It handles the serialization of recipe data for API responses and
    deserialization of incoming recipe data for creating/updating recipes.
    """
    # Define the tags field using the TagSerializer
    # many=True allows multiple tags per recipe
    # required=False makes the field optional when creating/updating recipes
    tags = TagSerializer(many=True, required=False)

    class Meta:
        """Meta class defining the serializer configuration.
        
        Attributes:
            model: The Django model class to serialize
            fields: List of model fields to include in serialization
            read_only_fields: Fields that should not be modified via API
        """
        model = Recipe
        fields = [
            'id',        # Recipe identifier
            'title',     # Recipe title/name
            'time_minutes', # Time to prepare recipe
            'price',     # Recipe cost
            'link',      # URL to recipe details
            'tags'       # Associated tags
        ]
        read_only_fields = ['id']  # ID is auto-generated and should not be modified


    def _get_or_create_tags(self, tags, recipe):
        """Helper method to get or create tags and add them to a recipe."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)
            
    


    def create(self, validated_data):
        """Create a recipe with associated tags.
        
        This method handles:
        1. Extracting tags data from the validated input
        2. Creating the base recipe
        3. Creating or retrieving existing tags
        4. Associating tags with the recipe
        
        Args:
            validated_data: Dictionary of validated recipe data
            
        Returns:
            Recipe: The newly created recipe instance
        """
        # Extract tags data and remove from validated_data
        tags = validated_data.pop('tags', [])
        
        # Create the recipe instance without tags
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)
            
        return recipe
    

    def update(self, instance, validated_data):
        """Update a recipe with associated tags.
        
        This method handles:
        1. Extracting tags data from the validated input
        2. Updating the base recipe
        3. Creating or retrieving existing tags 
        
        Args:
            instance: The existing recipe instance to update
            validated_data: Dictionary of validated recipe data
            
        Returns:
            Recipe: The updated recipe instance
            
        """
        # Extract tags data and remove from validated_data
        tags = validated_data.pop('tags', None)
        
        

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
           
        return instance # Return the updated recipe instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
 
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
