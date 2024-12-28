"""
Serializers for the user API View.
"""

from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext as _
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
    
    def update(self, instance, validated_data):
        """Update and return a user with encrypted password.
        
        Args:
            instance: The existing user instance that needs to be updated
            validated_data: Dictionary containing the validated fields to update
            
        Returns:
            User: The updated user instance
        """
        # Extract the password from validated_data if it exists, otherwise None
        # Using pop() removes it from validated_data to prevent direct password update
        password = validated_data.pop('password', None)
        
        # Update all other user fields using the parent class's update method
        # This handles updating fields like email, name, etc.
        user = super().update(instance, validated_data)
        
        # If a new password was provided in the update request
        if password:
            # Use set_password to properly hash the new password
            # This is more secure than directly setting the password field
            user.set_password(password)
            # Save the user instance to persist the password change
            user.save()
            
        return user
    


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token.
    This serializer handles the validation of user credentials and authentication.
    It is used in the token-based authentication process.
    """
    # EmailField for user email with default validation
    email = serializers.EmailField()
    
    # CharField for password with specific styling and validation options
    password = serializers.CharField(
        style={'input_type': 'password'},  # Renders as password field in browsable API
        trim_whitespace=False,             # Preserves whitespace in password
    )

    def validate(self, attrs):
        """Validate and authenticate the user.
        
        Args:
            attrs (dict): Contains the validated fields (email and password)
            
        Returns:
            dict: The validated attributes with authenticated user object
            
        Raises:
            serializers.ValidationError: If authentication fails
        """
        # Extract email and password from the validated data
        email = attrs.get('email')
        password = attrs.get('password')

        # Attempt to authenticate the user using Django's authenticate function
        # The authenticate function checks if the credentials are valid
        user = authenticate(
            request=self.context.get('request'),  # Pass request for context
            username=email,                       # Django uses username field for auth
            password=password,                    # The provided password
        )

        # If authentication fails, user will be None
        if not user:
            # Translate the error message using Django's translation system
            msg = _('Unable to authenticate with provided credentials.')
            # Raise validation error with custom error code
            raise serializers.ValidationError(msg, code='authorization')
        
        # Add the authenticated user to the validated attributes
        attrs['user'] = user
        return attrs


