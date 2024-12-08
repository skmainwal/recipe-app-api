"""
Views for the user API.
"""

from rest_framework import generics
from user.serializers import UserSerializer

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
