import pytest
from unittest.mock import patch
from app import db
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile

from app.modules.conftest import login, logout 

@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        user_test = User.query.filter_by(email='user_profile_test@example.com').first()
        if not user_test:
            user_test = User(email='user_profile_test@example.com', password='test1234')
            db.session.add(user_test)
            db.session.commit()

        profile = UserProfile.query.filter_by(user_id=user_test.id).first()
        if not profile:
            profile = UserProfile(user_id=user_test.id, name="TestName", surname="TestSurname")
            db.session.add(profile)
            db.session.commit()

    yield test_client

# --- TEST DE ACCESO (AUTORIZACIÓN) ---

def test_access_unauthorized(test_client):
    """Prueba que usuarios no logueados no puedan entrar a editar."""
    response = test_client.get("/profile/edit")
    assert response.status_code == 302

def test_access_authorized(test_client):
    """Prueba que un usuario logueado pueda ver el formulario."""
    login(test_client, "user_profile_test@example.com", "test1234")
    
    response = test_client.get("/profile/edit")
    assert response.status_code == 200
    assert b"Edit profile" in response.data
    
    logout(test_client)

# --- TEST DE FUNCIONALIDAD (POST) ---

def test_update_profile_success(test_client):
    """Prueba una actualización exitosa de perfil."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.post("/profile/edit", data={
        'name': 'Juan',
        'surname': 'Perez',
        'orcid': '0000-0002-1825-0097',
        'affiliation': 'Universidad de Sevilla'
    }, follow_redirects=True)

    assert response.status_code == 200

    with test_client.application.app_context():
        user = User.query.filter_by(email='user_profile_test@example.com').first()
        assert user.profile.name == 'Juan'
        assert user.profile.surname == 'Perez'
        assert user.profile.affiliation == 'Universidad de Sevilla'

    logout(test_client)

# --- TEST DE VALIDACIONES (CASOS DE ERROR) ---

def test_invalid_orcid_format(test_client):
    """Prueba que el validador de ORCID rechace formatos incorrectos."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.post("/profile/edit", data={
        'name': 'Juan',
        'surname': 'Perez',
        'orcid': '1234-bad-orcid',
        'affiliation': 'Universidad de Sevilla'
    })

    assert response.status_code == 200
    assert b'Invalid ORCID' in response.data or b'match the format' in response.data

    logout(test_client)

def test_required_fields_empty(test_client):
    """Prueba que los campos obligatorios no se envíen vacíos."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.post("/profile/edit", data={
        'name': '',
        'surname': '',
        'orcid': '',
        'affiliation': 'Universidad'
    })

    assert response.status_code == 200
    assert b'This field is required' in response.data

    logout(test_client)

def test_length_validations(test_client):
    """Prueba los límites de caracteres."""
    login(test_client, "user_profile_test@example.com", "test1234")

    long_string = "a" * 101

    response = test_client.post("/profile/edit", data={
        'name': long_string, 
        'surname': 'Perez',
        'orcid': '',
        'affiliation': 'Universidad'
    })

    assert response.status_code == 200
    assert b'longer than' in response.data or b'between' in response.data

    logout(test_client)
    
# --- TEST PARA PROFILE SUMMARY ---

def test_my_profile_page(test_client):
    """Prueba el acceso a la página de resumen del perfil."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.get("/profile/summary")
    
    assert response.status_code == 200
    assert b"User profile" in response.data or b"Summary" in response.data

    logout(test_client)

# --- TESTS PARA 2FA (DOBLE FACTOR) ---

def test_2fa_enable_page_get(test_client):
    """Prueba la carga de la página para activar 2FA."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.get("/2fa/enable")
    
    assert response.status_code == 200
    assert b"data:image/png;base64" in response.data

    logout(test_client)

def test_2fa_enable_submit_success(test_client):
    """Prueba la activación exitosa de 2FA."""
    login(test_client, "user_profile_test@example.com", "test1234")

    with test_client.session_transaction() as sess:
        sess['totp_secret_pending'] = 'JBSWY3DPEHPK3PXP'

    with patch("pyotp.TOTP.verify", return_value=True):
        response = test_client.post("/2fa/enable", data={
            "verification_token": "123456"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"2FA activado correctamente" in response.data

    logout(test_client)
