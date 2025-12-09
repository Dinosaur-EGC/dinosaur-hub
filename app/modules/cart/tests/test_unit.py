import pytest
from app.modules.cart.services import CartService
from unittest.mock import MagicMock, patch

@pytest.fixture
def cart_service():
    service = CartService()
    service.cart_repository = MagicMock()
    service.hubfile_repository = MagicMock()
    service.hubfile_service = MagicMock()
    return service

#TEST PARA ADD_ITEM_TO_CART

def test_add_item_to_cart_success(cart_service):
    cart_service.hubfile_repository.get_by_id.return_value = True
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = None

    result, status = cart_service.add_item_to_cart(user_id=1, hubfile_id=101)

    assert status == 200
    assert result == {"message": "Item added successfully"}

    cart_service.cart_repository.create.assert_called_once()

def test_add_item_to_cart_hubfile_not_found(cart_service):
    cart_service.hubfile_repository.get_by_id.return_value = None

    result, status = cart_service.add_item_to_cart(user_id=1, hubfile_id=101)

    assert status == 404
    assert result == {"error": "Hubfile not found"}

    cart_service.cart_repository.create.assert_not_called()

def test_add_item_to_cart_already_in_cart(cart_service):
    cart_service.hubfile_repository.get_by_id.return_value = True
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = MagicMock()

    result, status = cart_service.add_item_to_cart(user_id=1, hubfile_id=101)

    assert status == 409
    assert result == {"message": "Item already in cart"}

    cart_service.cart_repository.create.assert_not_called()

def test_add_item_to_cart_database_error(cart_service):
    cart_service.hubfile_repository.get_by_id.return_value = True
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = None
    cart_service.cart_repository.create.side_effect = Exception("DB Error")

    result, status = cart_service.add_item_to_cart(user_id=1, hubfile_id=101)

    assert status == 500
    assert "Internal error" in result["error"]

    cart_service.cart_repository.session.rollback.assert_called_once()

#TEST PARA REMOVE_ITEM_FROM_CART

def test_remove_item_success(cart_service):
    mock_item = MagicMock()
    mock_item.id = 5
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = mock_item

    result, status = cart_service.remove_item_from_cart(user_id=1, hubfile_id=101)

    assert status == 200
    cart_service.cart_repository.delete.assert_called_once_with(mock_item.id)

def test_remove_item_not_found(cart_service):
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = None

    result, status = cart_service.remove_item_from_cart(user_id=1, hubfile_id=101)

    assert status == 404
    assert result == {"error": "Item not found in cart"}

    cart_service.cart_repository.delete.assert_not_called()

def test_remove_item_database_error(cart_service):
    cart_service.cart_repository.get_item_by_user_and_hubfile.return_value = MagicMock()
    cart_service.cart_repository.delete.side_effect = Exception("DB Error")

    result, status = cart_service.remove_item_from_cart(user_id=1, hubfile_id=101)

    assert status == 500
    assert "Internal error" in result["error"]
    cart_service.cart_repository.session.rollback.assert_called_once()

#TEST PARA GET_CART_ITEMS   

def test_get_cart_items(cart_service):
    mock_cart_items = [MagicMock(hubfile_id=201), MagicMock(hubfile_id=202)]
    cart_service.cart_repository.get_items_by_user.return_value = mock_cart_items

    mock_hubfiles = [MagicMock(id=201, name="Fossil 1"), MagicMock(id=202, name="Fossil 2")]
    cart_service.hubfile_repository.filter_by_ids.return_value = mock_hubfiles

    result = cart_service.get_cart_items(user_id=1)

    assert len(result) == 2
    assert result == mock_hubfiles

    cart_service.cart_repository.get_items_by_user.assert_called_once_with(1)
    cart_service.hubfile_repository.filter_by_ids.assert_called_once_with([201, 202])

def test_get_cart_items_empty(cart_service):
    cart_service.cart_repository.get_items_by_user.return_value = []

    cart_service.hubfile_repository.filter_by_ids.return_value = []

    result = cart_service.get_cart_items(user_id=1)

    assert result == []
    cart_service.cart_repository.get_items_by_user.assert_called_once_with(1)
    cart_service.hubfile_repository.filter_by_ids.assert_called_once_with([])

#TEST PARA GENERATE_CART_ZIP

def test_generate_cart_zip_success(cart_service):
    mock_cart_item = MagicMock()
    mock_cart_item.hubfile_id = 1
    cart_service.cart_repository.get_items_by_user.return_value = [mock_cart_item]

    mock_hubfile = MagicMock()
    mock_hubfile.name = "fossil_model.csv"
    cart_service.hubfile_repository.filter_by_ids.return_value = [mock_hubfile]

    cart_service.hubfile_service.get_path_by_hubfile.return_value = "/path/to/fossil_model.csv"

    with patch("app.modules.cart.services.os") as mock_os, \
         patch("app.modules.cart.services.tempfile") as mock_tempfile, \
         patch("app.modules.cart.services.zipfile") as mock_zipfile, \
         patch("app.modules.cart.services.datetime") as mock_datetime:

        mock_tempfile.mkdtemp.return_value = "/tmp/fake_dir"
        mock_os.path.join.return_value = "/tmp/fake_dir/dinosaurhub_dataset.zip"
        mock_os.path.exists.return_value = True

        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-06-01_12-00"
        mock_datetime.now.return_value = mock_now

        mock_zip_instance = MagicMock()
        mock_zipfile.ZipFile.return_value.__enter__.return_value = mock_zip_instance

        zip_path, zip_filename = cart_service.generate_cart_zip(user_id=1)

        assert zip_path == "/tmp/fake_dir/dinosaurhub_dataset.zip"
        assert zip_filename == "dinosauhub_dataset_2024-06-01_12-00.zip"

        mock_zip_instance.write.assert_called_with(
            "/path/to/fossil_model.csv", arcname="fossil_model.csv"
        )

def test_generate_zip_empty_cart(cart_service):
    cart_service.cart_repository.get_items_by_user.return_value = []

    cart_service.hubfile_repository.filter_by_ids.return_value = []

    with pytest.raises(ValueError, match="Cart is empty") :
        cart_service.generate_cart_zip(user_id=1)

#TEST PARA EMPTY_CART

def test_empty_cart_success(cart_service):
    result, status = cart_service.empty_cart(user_id=1)

    assert status == 200
    assert result == {"message": "Cart emptied successfully"}

    cart_service.cart_repository.delete_by_column.assert_called_once_with("user_id", 1)

def test_empty_cart_database_error(cart_service):
    cart_service.cart_repository.delete_by_column.side_effect = Exception("DB Error")

    result, status = cart_service.empty_cart(user_id=1)

    assert status == 500
    assert "Internal error" in result["error"]
