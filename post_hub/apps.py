"""
This module configures the Django application for the post_hub app.

Classes:
    PostHubConfig: Configures the post_hub app.
"""
from django.apps import AppConfig


class PostHubConfig(AppConfig):
    """
    Configures the post_hub app.

    Attributes:
        default_auto_field (str): The default auto field type for
                            the app's models.
        name (str): The name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'post_hub'
