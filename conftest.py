# conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """
    Cliente de DRF sin autenticar.
    Usado para endpoints públicos o para probar status 401.
    """
    return APIClient()

@pytest.fixture
def user(db):
    """
    Crea un usuario de prueba en la BD de tests.
    El fixture `db` habilita el acceso a la base de datos.
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="secret123"
    )

@pytest.fixture
def auth_client(api_client, user):
    """
    Cliente de DRF autenticado con el fixture `user`.
    Ideal para probar endpoints protegidos.
    """
    api_client.force_authenticate(user=user)
    return api_client
