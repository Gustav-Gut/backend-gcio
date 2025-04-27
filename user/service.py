from django.db import models
from django.core.paginator import Paginator

class UserService:
    @staticmethod
    def get_users(limit=50):
        from user.models import User  # Import the User model
        users = User.objects.all()[:limit]
        return users