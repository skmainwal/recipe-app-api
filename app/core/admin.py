"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _


# Custom UserAdmin class to define the admin interface for the User model
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']  # Order users by their ID in the admin interface
    list_display = ['email', 'name', 'is_active', 'is_staff']  # Fields to display in the user list view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Basic fields for user details
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),  # Permission-related fields
        (_('Important dates'), {'fields': ('last_login',)}),  # Field for important dates
    )
    readonly_fields = ['last_login']  # Make last_login field read-only
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # CSS class for styling the form
            'fields': ('email', 'password1', 'password2', 'name',
                       'is_active', 'is_staff', 'is_superuser')  # Fields for adding a new user
        }),
    )


# Register the User model with the custom UserAdmin class
admin.site.register(models.User, UserAdmin)
# Register the Recipe model with the default admin class
admin.site.register(models.Recipe)
# Register the Tag model with the default admin class
admin.site.register(models.Tag)
# Register the Ingredient model with the default admin class
admin.site.register(models.Ingredient)

