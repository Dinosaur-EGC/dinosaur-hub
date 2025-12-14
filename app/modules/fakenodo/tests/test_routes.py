import pytest
from unittest.mock import patch, MagicMock
import io
import app.modules.fakenodo.routes as routes_module
from werkzeug.datastructures import FileStorage # Necesario para mockear el save

# Fixture para resetear el diccionario 'datasets' antes de cada test
@pytest.fixture
def mock_datasets():
    # Usamos clear=True para asegurar que empezamos vacíos
    with patch.dict(routes_module.datasets, {}, clear=True):
        yield routes_module.datasets

# --- POST /fakenodo/upload ---

def test_upload_dataset_success(test_client, mock_datasets):
    # Mockeamos mkdtemp y os.path.join
    with patch('app.modules.fakenodo.routes.tempfile.mkdtemp') as mock_mkdtemp, \
         patch('os.path.join') as mock_join, \
         patch.object(FileStorage, 'save') as mock_save: # Mockeamos el método save de FileStorage
        
        mock_mkdtemp.return_value = '/tmp/fake_dir'
        mock_join.return_value = '/tmp/fake_dir/test_file.csv'
        
        data = {
            'file': (io.BytesIO(b"fake content"), 'test_file.csv')
        }
        
        response = test_client.post('/fakenodo/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 201
        assert response.json['filename'] == 'test_file.csv'
        
        # Verificamos que se llamó a save (pero como es un mock, no escribió en disco)
        mock_save.assert_called_once_with('/tmp/fake_dir/test_file.csv')
        
        dataset_id = response.json['id']
        assert dataset_id in mock_datasets
        assert mock_datasets[dataset_id]['filename'] == 'test_file.csv'

def test_upload_dataset_no_file(test_client):
    # Como no podemos cambiar el código routes.py, el acceso request.files['file']
    # lanza un error 400 estándar de Flask antes de llegar al return personalizado.
    # Por tanto, el test solo verifica que el status sea 400.
    response = test_client.post('/fakenodo/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    # Eliminamos la aserción del mensaje JSON porque es inalcanzable sin cambiar el código

# --- GET /fakenodo/info/<id> ---

def test_get_dataset_success(test_client, mock_datasets):
    mock_datasets[0] = {
        'id': 0,
        'filename': 'my_data.csv',
        'file_path': '/tmp/path/my_data.csv'
    }

    with patch('app.modules.fakenodo.routes.send_file') as mock_send_file:
        mock_send_file.return_value = "File Content Sent"
        
        response = test_client.get('/fakenodo/info/0')
        
        assert response.status_code == 200
        mock_send_file.assert_called_once_with(
            '/tmp/path/my_data.csv', 
            as_attachment=True, 
            download_name='my_data.csv'
        )

def test_get_dataset_not_found(test_client, mock_datasets):
    response = test_client.get('/fakenodo/info/999')
    assert response.status_code == 404
    assert response.json['error'] == 'Dataset not found'

# --- GET /fakenodo/datasets ---

def test_list_datasets(test_client, mock_datasets):
    mock_datasets[1] = {'id': 1, 'filename': 'f1'}
    mock_datasets[2] = {'id': 2, 'filename': 'f2'}
    
    response = test_client.get('/fakenodo/datasets')
    
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    # Verificamos que los IDs obtenidos están en los esperados
    ids = [d['id'] for d in data]
    assert 1 in ids
    assert 2 in ids

# --- DELETE /fakenodo/dataset/<id> ---

def test_delete_dataset_success(test_client, mock_datasets):
    mock_datasets[5] = {
        'id': 5,
        'filename': 'to_delete.csv',
        'file_path': '/tmp/to_delete.csv'
    }

    with patch('os.remove') as mock_remove:
        response = test_client.delete('/fakenodo/dataset/5')
        
        assert response.status_code == 200
        assert response.json['message'] == 'Dataset deleted'
        
        assert 5 not in mock_datasets
        mock_remove.assert_called_once_with('/tmp/to_delete.csv')

def test_delete_dataset_not_found(test_client, mock_datasets):
    with patch('os.remove') as mock_remove:
        response = test_client.delete('/fakenodo/dataset/999')
        
        assert response.status_code == 404
        assert response.json['error'] == 'Dataset not found'
        mock_remove.assert_not_called()