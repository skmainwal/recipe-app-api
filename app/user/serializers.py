"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        # Specify the model to be serialized
        model = get_user_model()
        # Define the fields to be included in the serialization
        fields = ['email', 'password', 'name']
        # Set extra options for the fields
        extra_kwargs = {
            'password': {
                'write_only': True,  # Password should not be readable
                'min_length': 5      # Minimum length for password
            }
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        # Use the custom create_user method to ensure the password is hashed
        return get_user_model().objects.create_user(**validated_data)
