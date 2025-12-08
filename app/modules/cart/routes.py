from flask import jsonify, render_template, request, flash, redirect, url_for, send_file    
from flask_login import current_user, login_required
from .services import CartService
from . import cart_bp

@cart_bp.route('/', methods=['GET'])
@login_required
def index():
    cart_service = CartService()
    cart_items = cart_service.get_cart_items(current_user.id)
    return render_template('cart/index.html', cart_items=cart_items)

@cart_bp.route('/add/<int:hubfile_id>', methods=['POST'])
@login_required
def add_to_cart(hubfile_id):

    cart_service = CartService()
    result, status = cart_service.add_item_to_cart(current_user.id, hubfile_id)

    if status == 200:
        items = cart_service.get_cart_items(current_user.id)
        result['cart_count'] = len(items)
    return jsonify(result), status 

@cart_bp.route('/remove/<int:hubfile_id>', methods=['POST'])
@login_required
def remove_from_cart(hubfile_id):
    cart_service = CartService()
    result, status = cart_service.remove_item_from_cart(current_user.id, hubfile_id)
    if not request.is_json:
        if status == 200:
            flash(result.get("message"), "success")
        else:
            flash(result.get("error"), "danger")
        return redirect(url_for('cart.index'))
    return jsonify(result), status

@cart_bp.route('/download', methods=['GET'])
@login_required
def download_cart():
    cart_service = CartService()
    try:
        zip_path, zip_filename = cart_service.generate_cart_zip(current_user.id)
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except ValueError as ve:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart.index'))
    except Exception as e:
        flash("An error occurred while generating the download.", "danger")
        return redirect(url_for('cart.index'))
