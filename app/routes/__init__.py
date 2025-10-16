# Package initialization file for routes module.
# This file makes the routes directory a Python package and allows
# importing route modules from the routes package.

from .recommendation import router as recommendation_router

__all__ = ["recommendation_router"]