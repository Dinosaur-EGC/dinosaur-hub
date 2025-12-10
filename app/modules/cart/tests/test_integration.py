import pytest
from app import db
from app.modules.hubfile.models import Hubfile
from app.modules.cart.models import ShoppingCartItem
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.fossils.models import FossilsFile
from app.modules.cart.services import CartService
from app.modules.auth.models import User

from unittest.mock import patch

EMAIL_TEST = "test@example.com"

# Helper para hacer login (reutilizando el usuario creado en conftest.py)
def login_user(test_client):
    user = User.query.filter_by(email=EMAIL_TEST).first()
    if not user:
        user = User(email=EMAIL_TEST, password="test1234")
        db.session.add(user)
        db.session.commit()
    
    test_client.post("/login", data={"email": EMAIL_TEST, "password": "test1234"}, follow_redirects=True)
    return user

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

def test_add_item_to_cart(test_client, sample_hubfile):
    cart_service = CartService()
    user = login_user(test_client)

    items_before = cart_service.get_cart_items(user.id)
    response = test_client.post(f"/cart/add/{sample_hubfile.id}")
    items_after = cart_service.get_cart_items(user.id)

    assert response.status_code == 200  
    assert response.json["message"] == "Item added successfully"
    assert response.json['cart_count'] == len(items_before) + 1 == len(items_after)

    item = ShoppingCartItem.query.filter_by(hubfile_id=sample_hubfile.id).first()
    assert item is not None
    assert item.user_id == 1

def test_add_item_duplicate(test_client, sample_hubfile):

    login_user(test_client)

    test_client.post(f"/cart/add/{sample_hubfile.id}")
    response = test_client.post(f"/cart/add/{sample_hubfile.id}")

    assert response.status_code == 409
    assert response.json["message"] == "Item already in cart"

def test_add_item_not_found(test_client):


    login_user(test_client)

    response = test_client.post(f"/cart/add/9999")  # ID que no existe

    assert response.status_code == 404
    assert response.json["error"] == "Hubfile not found"

def test_remove_item_from_cart(test_client, sample_hubfile):
    cart_service = CartService()
    user = login_user(test_client)

    items_before = cart_service.get_cart_items(user.id)
    test_client.post(f"/cart/add/{sample_hubfile.id}")
    items_after = cart_service.get_cart_items(user.id)
    
    response = test_client.post(f"/cart/remove/{sample_hubfile.id}", follow_redirects=True, json={})

    assert response.status_code == 200
    assert response.json["message"] == "Item removed successfully"
    assert response.json['cart_count'] == len(items_before) == len(items_after) - 1 

def test_remove_item_not_found(test_client):
    login_user(test_client)

    response = test_client.post(f"/cart/remove/9999", follow_redirects=True, json={})

    assert response.status_code == 404
    assert response.json["error"] == "Item not found in cart"

def test_empty_cart(test_client, sample_hubfile):
    login_user(test_client)
    test_client.post(f"/cart/add/{sample_hubfile.id}")

    response = test_client.post("/cart/empty", follow_redirects=True, json={})

    assert response.status_code == 200
    assert response.json["message"] == "Cart emptied successfully"
    assert response.json['cart_count'] == 0
    assert ShoppingCartItem.query.count() == 0

def test_empty_cart_when_already_empty(test_client):
    login_user(test_client)

    response = test_client.post("/cart/empty", follow_redirects=True, json={})

    assert response.status_code == 200
    assert response.json["message"] == "Cart emptied successfully"
    assert response.json['cart_count'] == 0
    assert ShoppingCartItem.query.count() == 0

def test_download_empty_cart(test_client):
    login_user(test_client)

    response = test_client.get("/cart/download", follow_redirects=True)

    assert response.status_code == 200
    assert b"Your cart is empty." in response.data

def test_download_cart_success(test_client, sample_hubfile):
    user = login_user(test_client)

    test_client.post(f"/cart/add/{sample_hubfile.id}")

    with patch("app.modules.cart.services.CartService.generate_cart_zip") as mock_generate:

        mock_generate.return_value = ("/tmp/fake_dataset.zip", "dino_test.zip")

        with patch("app.modules.cart.routes.send_file") as mock_send_file:
            mock_send_file.return_value = "Contenido del ZIP simulado"

            response = test_client.get("/cart/download")

            assert response.status_code == 200
            mock_generate.assert_called_once_with(user.id)
            mock_send_file.assert_called_once_with("/tmp/fake_dataset.zip", as_attachment=True, download_name="dino_test.zip")
