import pytest
from unittest.mock import MagicMock, patch
from app.modules.fakenodo.services import FakenodoService

@pytest.fixture
def fakenodo_service():
    service = FakenodoService()
    # Mockeamos el repositorio inyectado en el __init__
    service.deposition_repository = MagicMock()
    return service

# --- TEST PARA CREATE_NEW_DEPOSITION ---

def test_create_new_deposition_success(fakenodo_service):
    # Usamos MagicMock() simple en lugar de spec=DSMetaData para evitar el error de contexto
    mock_ds_metadata = MagicMock()
    mock_ds_metadata.title = "Test Dinosaur Dataset"
    mock_ds_metadata.description = "A description"
    mock_ds_metadata.publication_type.value = "none"
    mock_ds_metadata.authors = []
    mock_ds_metadata.tags = "tag1, tag2"

    mock_deposition = MagicMock()
    mock_deposition.id = 123
    fakenodo_service.deposition_repository.create_new_deposition.return_value = mock_deposition

    result = fakenodo_service.create_new_deposition(mock_ds_metadata)

    assert result["id"] == 123
    assert result["message"] == "Deposition succesfully created in Fakenodo"
    assert result["metadata"]["title"] == "Test Dinosaur Dataset"
    # Verificamos lógica de upload_type
    assert result["metadata"]["upload_type"] == "dataset"
    
    fakenodo_service.deposition_repository.create_new_deposition.assert_called_once()

def test_create_new_deposition_publication_type(fakenodo_service):
    mock_ds_metadata = MagicMock()
    mock_ds_metadata.title = "Paper"
    mock_ds_metadata.description = "Desc"
    mock_ds_metadata.publication_type.value = "article"
    mock_ds_metadata.authors = []
    mock_ds_metadata.tags = ""

    mock_deposition = MagicMock()
    mock_deposition.id = 124
    fakenodo_service.deposition_repository.create_new_deposition.return_value = mock_deposition

    result = fakenodo_service.create_new_deposition(mock_ds_metadata)

    assert result["metadata"]["upload_type"] == "publication"
    assert result["metadata"]["publication_type"] == "article"

def test_create_new_deposition_error(fakenodo_service):
    mock_ds_metadata = MagicMock()
    mock_ds_metadata.publication_type.value = "none"
    mock_ds_metadata.authors = []
    
    fakenodo_service.deposition_repository.create_new_deposition.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as excinfo:
        fakenodo_service.create_new_deposition(mock_ds_metadata)
    
    assert "Failed to create deposition in Fakenodo with error: DB Error" in str(excinfo.value)

# --- TEST PARA UPLOAD_FILE ---

def test_upload_file_success(fakenodo_service):
    # Eliminamos spec=DataSet y spec=FossilsFile
    mock_dataset = MagicMock()
    mock_dataset.id = 10
    
    mock_fossils_file = MagicMock()
    mock_fossils_file.fossils_meta_data.csv_filename = "dino.csv"
    
    mock_user = MagicMock()
    mock_user.id = 5

    # Patcheamos las dependencias externas
    with patch("app.modules.fakenodo.services.os.path.getsize") as mock_getsize, \
         patch("app.modules.fakenodo.services.checksum") as mock_checksum, \
         patch("app.modules.fakenodo.services.uploads_folder_name") as mock_uploads_folder:
        
        mock_uploads_folder.return_value = "/tmp/uploads"
        mock_getsize.return_value = 1024
        mock_checksum.return_value = "hash123"

        result = fakenodo_service.upload_file(mock_dataset, 123, mock_fossils_file, user=mock_user)

        assert result["id"] == 123
        assert result["file"] == "dino.csv"
        assert result["fileSize"] == 1024
        assert result["checksum"] == "hash123"
        assert result["message"] == "File Uploaded to deposition with id 123"

# --- TEST PARA PUBLISH_DEPOSITION ---

def test_publish_deposition_success(fakenodo_service):
    # IMPORTANTE: Patcheamos la clase 'Deposition' en el módulo services.
    # Al patchear la clase completa, 'Deposition.query' será un mock y no intentará conectar a la BD.
    with patch("app.modules.fakenodo.services.Deposition") as mock_deposition_class:
        mock_deposition_instance = MagicMock()
        mock_deposition_instance.id = 123
        
        # Configuramos que Deposition.query.get(id) devuelva nuestra instancia mockeada
        mock_deposition_class.query.get.return_value = mock_deposition_instance

        result = fakenodo_service.publish_deposition(123)

        assert result["status"] == "published"
        assert result["conceptdoi"] == "fakenodo.doi.123"
        
        # Verificamos que se modificó el objeto mockeado
        assert mock_deposition_instance.status == "published"
        assert mock_deposition_instance.doi == "fakenodo.doi.123"
        # Verificamos que se llamó al repositorio para guardar
        fakenodo_service.deposition_repository.update.assert_called_once_with(mock_deposition_instance)

def test_publish_deposition_not_found(fakenodo_service):
    with patch("app.modules.fakenodo.services.Deposition") as mock_deposition_class:
        # Simulamos que no se encuentra nada
        mock_deposition_class.query.get.return_value = None

        with pytest.raises(Exception) as excinfo:
            fakenodo_service.publish_deposition(999)
        
        assert "Error 404: Deposition not found" in str(excinfo.value)
        fakenodo_service.deposition_repository.update.assert_not_called()

def test_publish_deposition_error(fakenodo_service):
    with patch("app.modules.fakenodo.services.Deposition") as mock_deposition_class:
        mock_deposition_instance = MagicMock()
        mock_deposition_class.query.get.return_value = mock_deposition_instance
        
        # Simulamos fallo en el repositorio
        fakenodo_service.deposition_repository.update.side_effect = Exception("Update fail")

        with pytest.raises(Exception) as excinfo:
            fakenodo_service.publish_deposition(123)
        
        assert "Failed to publish deposition with errors: Update fail" in str(excinfo.value)

# --- TEST PARA GET_DEPOSITION ---

def test_get_deposition_success(fakenodo_service):
    with patch("app.modules.fakenodo.services.Deposition") as mock_deposition_class:
        mock_deposition_instance = MagicMock()
        mock_deposition_instance.id = 123
        mock_deposition_instance.doi = "doi.123"
        mock_deposition_instance.dep_metadata = {"title": "Test"}
        mock_deposition_instance.status = "published"
        
        mock_deposition_class.query.get.return_value = mock_deposition_instance

        result = fakenodo_service.get_deposition(123)

        assert result["id"] == 123
        assert result["doi"] == "doi.123"
        assert result["status"] == "published"
        assert result["metadata"] == {"title": "Test"}

def test_get_deposition_not_found(fakenodo_service):
    with patch("app.modules.fakenodo.services.Deposition") as mock_deposition_class:
        mock_deposition_class.query.get.return_value = None

        with pytest.raises(Exception) as excinfo:
            fakenodo_service.get_deposition(999)
        
        assert "Deposition not found" in str(excinfo.value)

# --- TEST PARA GET_DOI ---

def test_get_doi_success(fakenodo_service):
    # Mockeamos el método get_deposition del propio servicio para aislar este test
    with patch.object(fakenodo_service, 'get_deposition') as mock_get_dep:
        mock_get_dep.return_value = {"doi": "fakenodo.doi.555"}
        
        doi = fakenodo_service.get_doi(555)
        
        assert doi == "fakenodo.doi.555"
        mock_get_dep.assert_called_once_with(555)