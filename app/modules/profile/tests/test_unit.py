import pytest
from unittest.mock import MagicMock, patch
from app.modules.profile.services import UserProfileService

@pytest.fixture
def profile_service():
    # Instanciamos el servicio
    service = UserProfileService()
    # Mockeamos el repositorio (aunque BaseService lo usa, es buena práctica tenerlo mockeado)
    service.repository = MagicMock()
    return service

# TEST PARA UPDATE_PROFILE

def test_update_profile_success(profile_service):
    # Mock del formulario
    mock_form = MagicMock()
    mock_form.validate.return_value = True
    mock_form.data = {"bio": "New bio", "name": "New Name"}
    
    # Mockeamos el método 'update' que viene heredado de BaseService
    # para aislar la prueba y verificar solo la lógica de update_profile
    profile_service.update = MagicMock(return_value="updated_instance")

    # Ejecución
    instance, errors = profile_service.update_profile(user_profile_id=1, form=mock_form)

    # Aserciones
    assert instance == "updated_instance"
    assert errors is None
    
    # Verificamos que se llamó a validate
    mock_form.validate.assert_called_once()
    
    # Verificamos que se llamó a self.update con los argumentos desempaquetados (**form.data)
    profile_service.update.assert_called_once_with(1, bio="New bio", name="New Name")

def test_update_profile_validation_failure(profile_service):
    # Mock del formulario que falla la validación
    mock_form = MagicMock()
    mock_form.validate.return_value = False
    mock_form.errors = {"bio": ["Too long"]}
    
    # Mockeamos update
    profile_service.update = MagicMock()

    # Ejecución
    instance, errors = profile_service.update_profile(user_profile_id=1, form=mock_form)

    # Aserciones
    assert instance is None
    assert errors == {"bio": ["Too long"]}
    
    # Verificamos que NO se llamó a update porque falló la validación
    profile_service.update.assert_not_called()

# TEST PARA GET_USER_PROFILE

def test_get_user_profile_found(profile_service):
    # CORRECCIÓN: Apuntamos al origen real del modelo User
    with patch("app.modules.auth.models.User") as MockUser:
        mock_user_instance = MagicMock()
        mock_user_instance.profile = "User Profile Data"
        
        # Configuramos el mock de la query de SQLAlchemy
        MockUser.query.get.return_value = mock_user_instance

        # Ejecución
        result = profile_service.get_user_profile(user_id=1)

        # Aserciones
        assert result == "User Profile Data"
        MockUser.query.get.assert_called_once_with(1)

def test_get_user_profile_not_found(profile_service):
    # CORRECCIÓN: Apuntamos al origen real del modelo User
    with patch("app.modules.auth.models.User") as MockUser:
        # Configuramos que query.get devuelva None (no se encontró usuario)
        MockUser.query.get.return_value = None

        # Ejecución
        result = profile_service.get_user_profile(user_id=999)

        # Aserciones
        assert result is None
        MockUser.query.get.assert_called_once_with(999)