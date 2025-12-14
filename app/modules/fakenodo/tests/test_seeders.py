import pytest
from unittest.mock import MagicMock, patch
from app.modules.fakenodo.seeders import seed_depositions

def test_seed_depositions_empty():
    # Simulamos que Deposition y db son mocks para no tocar la BD real
    with patch('app.modules.fakenodo.seeders.Deposition') as mock_deposition, \
         patch('app.modules.fakenodo.seeders.db') as mock_db:
        
        # Configuramos para que count() devuelva 0 (tabla vacía)
        mock_deposition.query.count.return_value = 0
        
        seed_depositions()
        
        # Verificamos que se intentó guardar y confirmar cambios
        mock_db.session.bulk_save_objects.assert_called_once()
        mock_db.session.commit.assert_called_once()

def test_seed_depositions_already_populated():
    with patch('app.modules.fakenodo.seeders.Deposition') as mock_deposition, \
         patch('app.modules.fakenodo.seeders.db') as mock_db:
        
        # Configuramos para que count() devuelva 5 (tabla con datos)
        mock_deposition.query.count.return_value = 5
        
        seed_depositions()
        
        # Verificamos que NO se hizo nada
        mock_db.session.bulk_save_objects.assert_not_called()
        mock_db.session.commit.assert_not_called()