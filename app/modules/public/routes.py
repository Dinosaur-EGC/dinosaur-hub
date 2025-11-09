import logging

from flask import render_template
from app.modules.dataset.services import DataSetService
from app.modules.featuremodel.services import FeatureModelService
from app.modules.public import public_bp

from flask import redirect, url_for, request
from flask_login import current_user
from app.modules.profile.services import UserProfileService
from app.modules.dataset.models import DataSet
from app.modules.auth.models import User  #
from app import db


logger = logging.getLogger(__name__)


@public_bp.route("/")
def index():
    """
    Ruta principal (la que ya tenías).
    """
    logger.info("Access index")
    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()


    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()


    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_feature_model_downloads = feature_model_service.total_feature_model_downloads()

    total_dataset_views = dataset_service.total_dataset_views()
    total_feature_model_views = feature_model_service.total_feature_model_views()

    return render_template(
        "public/index.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=datasets_counter,
        feature_models_counter=feature_models_counter,
        total_dataset_downloads=total_dataset_downloads,
        total_feature_model_downloads=total_feature_model_downloads,
        total_dataset_views=total_dataset_views,
        total_feature_model_views=total_feature_model_views,
    )



@public_bp.route("/user/<int:user_id>")
def view_user_profile(user_id):
    """
    Nueva ruta para ver el perfil público de un usuario.
    """
    logger.info(f"Access user profile: {user_id}")
    
    
    if current_user.is_authenticated and user_id == current_user.id:
        return redirect(url_for('profile.my_profile'))

   
    profile_service = UserProfileService()
    user_profile = profile_service.get_user_profile(user_id) # Usamos el servicio de perfil
    
    if not user_profile:
        
        return render_template("404.html"), 404

   
    page = request.args.get('page', 1, type=int)
    per_page = 5  

    user_datasets_pagination = db.session.query(DataSet) \
        .filter(DataSet.user_id == user_id) \
        .order_by(DataSet.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    total_datasets_count = db.session.query(DataSet) \
        .filter(DataSet.user_id == user_id) \
        .count()

    
    return render_template(
        "profile/view_profile.html",
        user_profile=user_profile,
        user=user_profile.user, 
        datasets=user_datasets_pagination.items,
        pagination=user_datasets_pagination,
        total_datasets=total_datasets_count
    )