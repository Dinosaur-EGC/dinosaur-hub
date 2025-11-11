from .repositories import ShoppingCartItemRepository
from app.modules.hubfile.repositories import HubfileRepository

class CartService:
    def __init__(self):
        self.cart_repository = ShoppingCartItemRepository()
        self.hubfile_repository = HubfileRepository()

    def add_item_to_cart(self, user_id, hubfile_id):
        if not self.hubfile_repository.get_by_id(hubfile_id):
            return {"error": "Hubfile not found"}, 404
        
        existing = self.cart_repository.get_item_by_user_and_hubfile(user_id, hubfile_id)

        if existing:
            return {"message": "Item already in cart"}, 409
        
        try:
            # Usar el método create del repositorio o base de datos si es necesario
            new_item = self.cart_repository.create(
                user_id=user_id, hubfile_id=hubfile_id, commit=True
            )
            return {"message": "Item added successfully"}, 200
        except Exception as e:
            self.cart_repository.session.rollback() # Usar la sesión del repositorio
            return {"error": f"Internal error: {e}"}, 500
    
    def get_cart_items(self, user_id):
        # 1. Obtiene los ítems del carrito (los objetos ShoppingCartItem)
        cart_items = self.cart_repository.get_items_by_user(user_id)
        hubfile_ids = [item.hubfile_id for item in cart_items]
        
        # 2. Recupera los objetos Hubfile reales
        selected_hubfiles = self.hubfile_repository.filter_by_ids(hubfile_ids)
        return selected_hubfiles