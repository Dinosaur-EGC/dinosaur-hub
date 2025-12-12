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