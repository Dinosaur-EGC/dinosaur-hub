
from app.modules.cart.models import ShoppingCartItem
from core.repositories.BaseRepository import BaseRepository

class ShoppingCartItemRepository(BaseRepository):

    def __init__(self):
        super().__init__(ShoppingCartItem)

    def get_items_by_user(self, user_id):
        return self.model.query.filter_by(user_id =user_id).all()

    def get_item_by_user_and_hubfile(self, user_id, hubfile_id):
        return self.model.query.filter_by(user_id=user_id, hubfile_id=hubfile_id).first()
