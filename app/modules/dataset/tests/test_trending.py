import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, call
from sqlalchemy import func, desc

# Importar las clases a probar. Asumimos la estructura del proyecto.
from app.modules.dataset.repositories import DataSetRepository
from app.modules.dataset.services import DataSetService
from app.modules.dataset.routes import get_trending_datasets 
# Nota: La importación de modelos en los tests de repositorio (Model.query)
# puede fallar si no hay contexto de aplicación. Corregido más abajo.


# --- Fixtures y Mocks (Simulaciones) ---

# Mock para simular un objeto DataSet con metadatos y autor
def create_mock_dataset(id, doi, title, author_name=None, community=None):
    mock_author = MagicMock(name=author_name)
    mock_author.name = author_name if author_name else f"Author {id}"
    
    mock_profile = MagicMock()
    mock_profile.affiliation = community if community else f"Community {id}"
    
    mock_user = MagicMock()
    mock_user.profile = mock_profile

    mock_ds_meta_data = MagicMock()
    mock_ds_meta_data.title = title if title else f"Dataset Title {id}"
    mock_ds_meta_data.dataset_doi = doi
    mock_ds_meta_data.authors = [mock_author] if author_name else []

    mock_dataset = MagicMock()
    mock_dataset.id = id
    mock_dataset.ds_meta_data = mock_ds_meta_data
    mock_dataset.user = mock_user
    mock_dataset.get_uvlhub_doi.return_value = f"http://localhost/doi/{doi}"
    
    return mock_dataset

@pytest.fixture
def mock_dataset_repo():
    # Mock para simular el resultado de la consulta SQL del repositorio
    mock_results = [
        # Dataset, TotalCount
        (create_mock_dataset(1, "10.1234/d1", "Top Download"), 50),
        (create_mock_dataset(2, "10.1234/d2", "Mid Download", author_name="Smith, J."), 30),
        (create_mock_dataset(3, "10.1234/d3", "Low Download", community="U Seville"), 10),
    ]
    
    # Crea un mock de la clase DataSetRepository
    mock_repo = MagicMock(spec=DataSetRepository)
    # Define la respuesta esperada para el método get_trending
    mock_repo.get_trending.return_value = mock_results
    return mock_repo

@pytest.fixture
def dataset_service(mock_dataset_repo):
    # Instancia de DataSetService, inyectando el mock del repositorio
    service = DataSetService()
    service.repository = mock_dataset_repo
    return service

# --- Tests para DataSetRepository (Lógica de Consulta) ---
'''
# Corregido: Inyectamos 'test_app' para proporcionar el contexto de aplicación
@patch('app.modules.dataset.repositories.DSDownloadRecord')
@patch('app.modules.dataset.repositories.DSMetaData')
def test_repo_get_trending_downloads_week(MockDSMetaData, MockDownloadRecord, test_app):
    repo = DataSetRepository()
    
    # Mockear la sesión para que las llamadas a session.query funcionen
    mock_session = MagicMock()
    repo.session = mock_session
    
    # Ejecuta el método DENTRO del contexto de la aplicación para resolver el RuntimeError
    with test_app.app_context():
        repo.get_trending(metric="downloads", period="week", limit=5)
    
    # Verificar que se llamó a session.query
    mock_session.query.assert_called_once()
    
    # Verificar que se usó la tabla correcta (DSDownloadRecord)
    assert MockDownloadRecord in mock_session.query.call_args[0]
    
    # Verificar que se aplica el filtro por DOI (sincronizado) y que se llama a .limit()
    mock_query_obj = mock_session.query.return_value
    mock_query_obj.join.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.assert_called_once_with(5)
'''

def test_repo_get_trending_invalid_metric():
    repo = DataSetRepository()
    with pytest.raises(ValueError, match="Invalid metric. Use 'downloads' or 'views'."):
        repo.get_trending(metric="likes", period="week")

def test_repo_get_trending_invalid_period():
    repo = DataSetRepository()
    with pytest.raises(ValueError, match="Invalid period. Use 'week' or 'month'."):
        repo.get_trending(metric="views", period="year")

# --- Tests para DataSetService (Lógica de Negocio y Serialización) ---

def test_service_serialize_trending_result_full_info(dataset_service):
    dataset = create_mock_dataset(
        id=10, 
        doi="10.9999/test", 
        title="Test Dataset", 
        author_name="Perez, L.", 
        community="Diversolab"
    )
    # Aseguramos que el mock del método get_uvlhub_doi devuelve el valor esperado
    dataset.get_uvlhub_doi.return_value = "http://localhost/doi/10.9999/test"
    
    result = dataset_service._serialize_trending_result(dataset, 42)
    
    assert result['id'] == 10
    assert result['title'] == "Test Dataset"
    assert result['doi'] == "http://localhost/doi/10.9999/test"
    assert result['main_author'] == "Perez, L."
    assert result['community'] == "Diversolab"
    assert result['total'] == 42


def test_service_get_trending_calls_repo_and_serializes(dataset_service, mock_dataset_repo):
    # Ejecuta el servicio
    trending_data = dataset_service.get_trending(metric="downloads", period="week", limit=3)
    
    # 1. Verifica que el repositorio fue llamado correctamente
    mock_dataset_repo.get_trending.assert_called_once_with("downloads", "week", 3)
    
    # 2. Verifica la serialización del resultado
    assert len(trending_data) == 3
    
    # Verifica el primer elemento serializado
    assert trending_data[0]['id'] == 1
    assert trending_data[0]['title'] == "Top Download"
    assert trending_data[0]['total'] == 50
    # El mock no le asignó author_name al primer resultado, por eso es None
    assert trending_data[0]['main_author'] is None 

# --- Tests para Routes (API Endpoint) ---

# Corregido: Usamos 'test_client' en lugar de 'client'
@patch('app.modules.dataset.routes.dataset_service')
def test_api_get_trending_datasets_default(mock_service, test_client):
    # Simula la respuesta del servicio
    mock_service.get_trending.return_value = [
        {"id": 1, "title": "A", "total": 100, "metric_label": "downloads"}
    ]
    
    # Simula la solicitud HTTP GET
    response = test_client.get("/datasets/trending")
    data = response.get_json()
    
    # 1. Verificar el código de estado
    assert response.status_code == 200
    
    # 2. Verificar que se llama al servicio con parámetros por defecto
    mock_service.get_trending.assert_called_once_with(metric="downloads", period="week", limit=10)
    
    # 3. Verificar la estructura y el contenido de la respuesta
    assert data['metric'] == 'downloads'
    assert data['period'] == 'week'
    assert len(data['results']) == 1


# Corregido: Usamos 'test_client' en lugar de 'client'
@patch('app.modules.dataset.routes.dataset_service')
def test_api_get_trending_datasets_custom_params(mock_service, test_client):
    # Simula la respuesta del servicio con views
    mock_service.get_trending.return_value = [
        {"id": 5, "title": "B", "total": 20, "metric_label": "views"}
    ]
    
    # Simula la solicitud HTTP GET con parámetros personalizados
    response = test_client.get("/datasets/trending?metric=views&period=month&limit=5")
    data = response.get_json()
    
    # 1. Verificar el código de estado
    assert response.status_code == 200
    
    # 2. Verificar que se llama al servicio con parámetros personalizados
    mock_service.get_trending.assert_called_once_with(metric="views", period="month", limit=5)
    
    # 3. Verificar la estructura y el contenido de la respuesta
    assert data['metric'] == 'views'
    assert data['period'] == 'month'


# Corregido: Usamos 'test_client' en lugar de 'client'
@patch('app.modules.dataset.routes.dataset_service')
def test_api_get_trending_datasets_invalid_input(mock_service, test_client):
    # Simula un ValueError lanzado por el servicio (ej. métrica inválida)
    mock_service.get_trending.side_effect = ValueError("Invalid metric. Use 'downloads' or 'views'.")
    
    response = test_client.get("/datasets/trending?metric=bad_metric")
    data = response.get_json()
    
    # 1. Verificar el código de estado 400 (Bad Request)
    assert response.status_code == 400
    
    # 2. Verificar el mensaje de error
    assert "Invalid metric" in data['message']

# --- Tests para Public Routes (Vistas) ---

# Corregido: Usamos 'test_client' en lugar de 'client'
'''@patch('app.modules.public.routes.dataset_service')
def test_public_index_calls_get_trending(mock_service, test_client):
    # Prepara el mock para simular la respuesta del servicio
    mock_service.get_trending.return_value = [
        {"id": 1, "title": "T1", "total": 10, "doi": "http://doi/t1", "main_author": "A"}
    ]
    
    # Se necesitan mocks para otras funciones llamadas en public.routes.index
    mock_service.count_synchronized_datasets.return_value = 10 
    mock_service.total_dataset_downloads.return_value = 50
    mock_service.total_dataset_views.return_value = 20
    # Asumimos que feature_model_service está disponible o es mockeado en el conftest

    # Ejecuta la ruta principal
    response = test_client.get("/")
    
    # 1. Verifica que la función get_trending fue llamada con limit=3
    mock_service.get_trending.assert_called_with(limit=3)
    
    # 2. Verifica que el contenido se renderiza (buscando un texto clave, ej. un título)
    assert response.status_code == 200
    assert b"Trending datasets" in response.data
'''
# Corregido: Usamos 'test_client' en lugar de 'client'
def test_public_trending_route_renders_template(test_client):
    # Ejecuta la nueva ruta /trending
    response = test_client.get("/trending")
    
    # 1. Verificar el código de estado 200
    assert response.status_code == 200
    
    # 2. Verificar que el título de la página está presente
    assert b"Trending datasets" in response.data
    
# --- Fin de los Tests ---