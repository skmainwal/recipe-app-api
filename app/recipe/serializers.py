"""Serializers for recipe API."""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes.
    
    This serializer converts Recipe model instances to/from JSON format.
    It handles the serialization of recipe data for API responses and
    deserialization of incoming recipe data for creating/updating recipes.
    """

    class Meta:
        """Meta class defining the serializer configuration.
        
        Attributes:
            model: The Django model class to serialize
            fields: List of model fields to include in serialization
            read_only_fields: Fields that should not be modified via API
        """
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']  # Fields exposed in the API
        read_only_fields = ['id']  # ID is auto-generated and should not be modified
