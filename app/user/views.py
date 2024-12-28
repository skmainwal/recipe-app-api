"""
Views for the user API.
"""

from rest_framework import generics
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
