# seed/tests/test_views.py
import pytest
from django.urls import reverse
from seed.services import SeedServices

@pytest.mark.django_db
def test_recover_all_portal_types_empty(api_client, monkeypatch):
    # Parcheamos el servicio para que devuelva siempre []
    monkeypatch.setattr(SeedServices, 'get_portal_type', lambda: [])
    # Ajusta el nombre del reverse si tu basename o ruta difiere
    response = api_client.get("/api/seed/recover-portal-types/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.django_db
def test_recover_one_portal_types_empty(api_client, monkeypatch):
    monkeypatch.setattr(SeedServices, 'get_portal_type', lambda: [])
    response = api_client.get("/api/seed/recover-one-portal-types/")
    assert response.status_code == 200
    assert response.json() == []
