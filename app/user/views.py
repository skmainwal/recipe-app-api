"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from user.serializers import (UserSerializer, AuthTokenSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    # This view uses the CreateAPIView from Django REST Framework, which provides
    # the functionality to handle HTTP POST requests for creating a new instance
    # of a model. It automatically handles the request, validates the data using
    # the serializer, and saves the new user to the database if the data is valid.

    serializer_class = UserSerializer
    # The serializer_class attribute specifies the serializer that should be used
    # for validating and deserializing input, and for serializing output. Here, it
    # uses the UserSerializer to handle user data.


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    # The serializer_class attribute specifies the serializer that should be used
    # for validating and deserializing input, and for serializing output. Here, it
    # uses the AuthTokenSerializer to handle user authentication.

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    # The renderer_classes attribute specifies the renderer classes that should be used
    # for rendering the response. Here, it uses the default renderer classes provided by
    # Django REST Framework.


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user.
    
    This view inherits from RetrieveUpdateAPIView which provides GET and PATCH/PUT
    methods for retrieving and updating a user's details. This means users can:
    - GET their own details
    - Update their own details
    """
    serializer_class = UserSerializer
    # Specifies the serializer to convert user objects to/from JSON
    # Uses the same UserSerializer as CreateUserView

    authentication_classes = [authentication.TokenAuthentication]
    # Defines how users should authenticate themselves
    # TokenAuthentication expects requests to include an auth token in header:
    # Authorization: Token <token-value>

    permission_classes = [permissions.IsAuthenticated]
    # Specifies that only authenticated users can access this view
    # If user is not authenticated, they will get a 401 Unauthorized response

    def get_object(self):
        """Retrieve and return the authenticated user.
        
        This method is called by the view to get the object to operate on.
        Instead of looking up an object by ID, it returns the currently
        authenticated user from the request.
        """
        return self.request.user    
