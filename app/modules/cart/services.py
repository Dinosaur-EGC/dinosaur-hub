import os 
import tempfile
import zipfile
from flask import send_file

from .repositories import ShoppingCartItemRepository
from app.modules.hubfile.repositories import HubfileRepository
from app.modules.hubfile.services import HubfileService

class CartService:
    def __init__(self):
        self.cart_repository = ShoppingCartItemRepository()
        self.hubfile_repository = HubfileRepository()
        self.hubfile_service = HubfileService()

    def add_item_to_cart(self, user_id, hubfile_id):
        if not self.hubfile_repository.get_by_id(hubfile_id):
            return {"error": "Hubfile not found"}, 404
        
        existing = self.cart_repository.get_item_by_user_and_hubfile(user_id, hubfile_id)

        if existing:
            return {"message": "Item already in cart"}, 409
        
        try:
            self.cart_repository.create(
                user_id=user_id, hubfile_id=hubfile_id, commit=True
            )
            return {"message": "Item added successfully"}, 200
        except Exception as e:
            self.cart_repository.session.rollback() 
            return {"error": f"Internal error: {e}"}, 500
    
    def remove_item_from_cart(self, user_id, hubfile_id):

        existing = self.cart_repository.get_item_by_user_and_hubfile(user_id, hubfile_id)

        if not existing:
            return {"error": "Item not found in cart"}, 404
        
        try:
            self.cart_repository.delete(existing.id)
            
            return {"message": "Item removed successfully"}, 200
        except Exception as e:
            self.cart_repository.session.rollback() 
            return {"error": f"Internal error: {e}"}, 500


    def get_cart_items(self, user_id):
        cart_items = self.cart_repository.get_items_by_user(user_id)
        hubfile_ids = [item.hubfile_id for item in cart_items]
        
        selected_hubfiles = self.hubfile_repository.filter_by_ids(hubfile_ids)
        return selected_hubfiles

    def generate_cart_zip(self, user_id):
        cart_items = self.get_cart_items(user_id)
        
        if not cart_items:
            return {"error": "Cart is empty"}, 404

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"cart_user_{user_id}.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for hubfile in cart_items:
                file_path = self.hubfile_service.get_path_by_hubfile(hubfile.id)
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=hubfile.name)
                else:
                    print(f"File {file_path} does not exist and will be skipped.")

        return zip_path