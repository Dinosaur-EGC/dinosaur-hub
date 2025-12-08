from core.blueprints.base_blueprint import BaseBlueprint
from flask_login import current_user

cart_bp = BaseBlueprint("cart", __name__, template_folder="templates", url_prefix='/cart')

@cart_bp.app_context_processor
def inject_cart_count():
    cart_count = 0
    if current_user.is_authenticated:
        try:
            from .services import CartService
            service = CartService()
            items = service.get_cart_items(current_user.id)
            cart_count = len(items)
        except Exception:
            cart_count = 0
    return {'cart_count': cart_count}