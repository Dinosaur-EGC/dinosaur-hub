import pytest
import pyotp
from flask import session, url_for
from app import db
from app.modules.auth.models import User
from app.modules.auth.services import AuthenticationService

@pytest.fixture(scope='module')
def test_client(test_client):
    """Extiende el fixture del cliente para incluir el contexto de la app si es necesario"""
    yield test_client

@pytest.fixture(scope='module')
def auth_service():
    return AuthenticationService()

@pytest.fixture(scope='function')
def user_with_2fa(test_client):
    """Crea un usuario temporal con 2FA activado para los tests"""
    user = User(email="test2fa@example.com", password="password123")
    user.totp_secret = pyotp.random_base32()
    db.session.add(user)
    db.session.commit()
    yield user
    # Cleanup
    db.session.delete(user)
    db.session.commit()

def test_user_totp_methods(user_with_2fa):
    """Prueba los métodos del modelo User relacionados con TOTP"""
    # Test URI generation
    uri = user_with_2fa.get_totp_uri()
    assert "otpauth://totp/Dinosaur%20Hub:test2fa%40example.com" in uri
    assert user_with_2fa.totp_secret in uri

    # Test verificación de token
    totp = pyotp.TOTP(user_with_2fa.totp_secret)
    valid_token = totp.now()
    assert user_with_2fa.verify_totp(valid_token) is True
    assert user_with_2fa.verify_totp("000000") is False

def test_login_redirects_to_2fa(test_client, user_with_2fa):
    """Verifica que al hacer login con un usuario 2FA, redirige al formulario de verificación"""
    response = test_client.post(url_for('auth.login'), data={
        'email': user_with_2fa.email,
        'password': 'password123'
    })
    
    # Debe redirigir, no hacer login directo (código 302)
    assert response.status_code == 302
    assert url_for('auth.verify_2fa') in response.location
    
    # Verificar que la sesión tiene el ID temporal
    with test_client.session_transaction() as sess:
        assert sess['2fa_user_id'] == user_with_2fa.id

def test_verify_2fa_success(test_client, user_with_2fa):
    """Prueba el flujo completo de verificación exitosa"""
    # 1. Pre-login para establecer sesión
    test_client.post(url_for('auth.login'), data={
        'email': user_with_2fa.email,
        'password': 'password123'
    })

    # 2. Generar token válido
    totp = pyotp.TOTP(user_with_2fa.totp_secret)
    token = totp.now()

    # 3. Enviar token
    response = test_client.post(url_for('auth.verify_2fa'), data={
        'token': token
    }, follow_redirects=True)

    assert response.status_code == 200