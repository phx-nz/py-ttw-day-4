# Import+export services so that they get added to the service registry.
# ServiceRegistry uses the AutoRegister feature of ``phx-class-registry``, so as soon as
# each class is imported, it gets added to the registry automatically.
# :see: https://class-registry.readthedocs.io/en/latest/advanced_topics.html
__all__ = [
    "ConfigService",
    "DatabaseService",
    "ProfileService",
    "get_service",
]
from services.base import get_service
from services.config import ConfigService
from services.database import DatabaseService
from services.profile import ProfileService
