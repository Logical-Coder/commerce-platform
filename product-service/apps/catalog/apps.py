# Import Django AppConfig class to configure this Django app
from django.apps import AppConfig


# Create configuration class for catalog app
class CatalogConfig(AppConfig):
    # Set default primary key type for models created in this app
    default_auto_field = "django.db.models.BigAutoField"

    # Tell Django the full Python path of this app
    name = "apps.catalog"