import pytest
from app import db
from app.modules.hubfile.models import Hubfile
from app.modules.cart.models import ShoppingCartItem
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.fossils.models import FossilsFile

# Helper para hacer login (reutilizando el usuario creado en conftest.py)
def login_user(test_client):
    test_client.post("/login", data={"email": "test@example.com", "password": "test1234"}, follow_redirects=True)

@pytest.fixture
def sample_hubfile(test_client):
    """Crea un Hubfile real en la BD de test para poder añadirlo al carrito."""
    # Necesitamos un Hubfile que exista para referenciarlo

    meta = DSMetaData(
        title="Test Dataset",
        description="Test Description",
        publication_type=PublicationType.NONE
    )
    db.session.add(meta)
    db.session.commit()

    dataset = DataSet(user_id=1, ds_meta_data_id=meta.id)
    db.session.add(dataset)
    db.session.commit()

    fossil_file = FossilsFile(data_set_id=dataset.id)
    db.session.add(fossil_file)
    db.session.commit()

    hubfile = Hubfile(name="test_dino.csv", checksum="dummy_checksum_123", size=1024, fossils_file_id=fossil_file.id)
    db.session.add(hubfile)
    db.session.commit()
    return hubfile

def test_cart_index_empty(test_client):
    """Prueba que la página del carrito carga vacía al principio."""
    login_user(test_client)
    
    response = test_client.get("/cart/")
    
    assert response.status_code == 200
    # Verificamos que no explote y que cargue el template (buscando un texto clave)
    assert b"My Custom Dataset Cart" in response.data and b"Your cart is empty" in response.data

def test_cart_index_displays_items(test_client, sample_hubfile):
    """Prueba que la página del carrito muestra los items añadidos."""
    login_user(test_client)


    # Añadimos un item al carrito en la BD de test
    test_client.post(f"/cart/add/{sample_hubfile.id}")
    
    response = test_client.get("/cart/")
     
    assert response.status_code == 200
    # Verificamos que el item añadido aparece en la página
    assert sample_hubfile.name.encode() in response.data

    assert b"Your cart is empty" not in response.data
    expected_action = f"/cart/remove/{sample_hubfile.id}".encode()
    assert expected_action in response.data