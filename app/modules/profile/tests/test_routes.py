import pytest
from app import db
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile

# Importamos los helpers de login/logout del conftest global
from app.modules.conftest import login, logout 

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extiende la fixture test_client para añadir datos específicos
    para este módulo (un usuario y su perfil).
    """
    # Creamos un contexto de aplicación para acceder a la BD
    with test_client.application.app_context():
        # 1. Crear usuario de prueba si no existe
        user_test = User.query.filter_by(email='user_profile_test@example.com').first()
        if not user_test:
            # CORREGIDO: Se ha eliminado 'is_developer=False' porque no existe en tu modelo
            user_test = User(email='user_profile_test@example.com', password='test1234')
            db.session.add(user_test)
            db.session.commit()

        # 2. Crear perfil asociado si no existe
        profile = UserProfile.query.filter_by(user_id=user_test.id).first()
        if not profile:
            profile = UserProfile(user_id=user_test.id, name="TestName", surname="TestSurname")
            db.session.add(profile)
            db.session.commit()

    yield test_client
    
    # Limpieza: En un entorno de testing real, la BD suele limpiarse sola al reiniciar,
    # pero si lo necesitas, aquí puedes borrar los datos creados.

# --- TEST DE ACCESO (AUTORIZACIÓN) ---

def test_access_unauthorized(test_client):
    """Prueba que usuarios no logueados no puedan entrar a editar."""
    response = test_client.get("/profile/edit")
    assert response.status_code == 302 # Redirección al login

def test_access_authorized(test_client):
    """Prueba que un usuario logueado pueda ver el formulario."""
    login(test_client, "user_profile_test@example.com", "test1234")
    
    response = test_client.get("/profile/edit")
    assert response.status_code == 200
    assert b"Edit profile" in response.data # Busca texto en el HTML devuelto
    
    logout(test_client)

# --- TEST DE FUNCIONALIDAD (POST) ---

def test_update_profile_success(test_client):
    """Prueba una actualización exitosa de perfil."""
    login(test_client, "user_profile_test@example.com", "test1234")

    # Enviamos datos válidos
    response = test_client.post("/profile/edit", data={
        'name': 'Juan',
        'surname': 'Perez',
        'orcid': '0000-0002-1825-0097',
        'affiliation': 'Universidad de Sevilla'
    }, follow_redirects=True)

    assert response.status_code == 200 # 200 porque seguimos el redirect

    # Verificar persistencia en Base de Datos
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
        'orcid': '1234-bad-orcid', # Formato inválido
        'affiliation': 'Universidad de Sevilla'
    })

    # Debe devolver 200 (se queda en la página) pero mostrar el error en el HTML
    assert response.status_code == 200
    # Buscamos alguna parte del mensaje de error típico de ORCID
    assert b'Invalid ORCID' in response.data or b'match the format' in response.data

    logout(test_client)

def test_required_fields_empty(test_client):
    """Prueba que los campos obligatorios no se envíen vacíos."""
    login(test_client, "user_profile_test@example.com", "test1234")

    response = test_client.post("/profile/edit", data={
        'name': '', # Obligatorio vacío
        'surname': '', # Obligatorio vacío
        'orcid': '',
        'affiliation': 'Universidad'
    })

    assert response.status_code == 200
    # WTForms suele devolver "This field is required"
    assert b'This field is required' in response.data

    logout(test_client)

def test_length_validations(test_client):
    """Prueba los límites de caracteres (ejemplo: max 100)."""
    login(test_client, "user_profile_test@example.com", "test1234")

    long_string = "a" * 101 # Cadena demasiado larga

    response = test_client.post("/profile/edit", data={
        'name': long_string, 
        'surname': 'Perez',
        'orcid': '',
        'affiliation': 'Universidad'
    })

    assert response.status_code == 200
    # Busca mensaje de error de longitud (depende de cómo hayas definido el mensaje en WTForms)
    # Puede ser 'Field cannot be longer than' o 'Field must be between'
    assert b'longer than' in response.data or b'between' in response.data

    logout(test_client)