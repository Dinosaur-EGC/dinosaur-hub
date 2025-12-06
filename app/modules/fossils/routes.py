from flask import render_template
from app.modules.fossils import fossils_bp


@fossils_bp.route('/fossils', methods=['GET'])
def index():
    return render_template('fossils/index.html')
