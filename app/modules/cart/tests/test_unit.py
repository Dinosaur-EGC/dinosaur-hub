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

    cart_service.cart_repository.create.assert_called_once()