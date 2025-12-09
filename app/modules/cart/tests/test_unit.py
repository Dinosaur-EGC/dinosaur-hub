import pytest
from app.modules.cart.services import CartService
from unittest.mock import MagicMock

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

