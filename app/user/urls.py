"""
URL mappings for the user API.
"""

from django.urls import path  # Import the path function to define URL patterns

from user import views  # Import views from the user app

# Define the app namespace for URL namespacing
app_name = 'user'

# URL patterns for the user app
urlpatterns = [
    # Map the 'create/' URL to the CreateUserView view
    # This URL will be used to create a new user
    path('create/', views.CreateUserView.as_view(), name='create'),

    # Map the 'token/' URL to the CreateTokenView view
    # This URL will be used to create an authentication token for a user
    path('token/', views.CreateTokenView.as_view(), name='token'),

    # Map the 'me/' URL to the ManageUserView view
    # This URL will be used to manage the authenticated user's profile
    path('me/', views.ManageUserView.as_view(), name='me'),
]
