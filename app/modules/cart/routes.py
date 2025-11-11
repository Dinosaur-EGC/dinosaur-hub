from flask import jsonify, render_template
from flask_login import current_user, login_required
from .services import CartService
from . import cart_bp


cart_service = CartService()

@cart_bp.route('/add/<int:hubfile_id>', methods=['POST'])
@login_required
def add_to_cart(hubfile_id):
    result, status = cart_service.add_item_to_cart(current_user.id, hubfile_id)
    return jsonify(result), status # Usa jsonify para la respuesta AJAX