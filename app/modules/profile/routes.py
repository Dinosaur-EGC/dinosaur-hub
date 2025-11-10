import io
import base64
import pyotp
import qrcode

from flask import redirect, render_template, request, url_for, flash, session
from flask_login import current_user, login_required

from app import db
from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet
from app.modules.profile import profile_bp
from app.modules.profile.forms import UserProfileForm
from app.modules.profile.services import UserProfileService
from app.modules.auth.forms import Enable2FAForm


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile
    if not profile:
        return redirect(url_for("public.index"))

    form = UserProfileForm()
    if request.method == "POST":
        service = UserProfileService()
        result, errors = service.update_profile(profile.id, form)
        return service.handle_service_response(
            result, errors, "profile.edit_profile", "Profile updated successfully", "profile/edit.html", form
        )

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/profile/summary")
@login_required
def my_profile():
    page = request.args.get("page", 1, type=int)
    per_page = 5

    user_datasets_pagination = (
        db.session.query(DataSet)
        .filter(DataSet.user_id == current_user.id)
        .order_by(DataSet.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    total_datasets_count = db.session.query(DataSet).filter(DataSet.user_id == current_user.id).count()

    print(user_datasets_pagination.items)

    return render_template(
        "profile/summary.html",
        user_profile=current_user.profile,
        user=current_user,
        datasets=user_datasets_pagination.items,
        pagination=user_datasets_pagination,
        total_datasets=total_datasets_count,
    )

@profile_bp.route("/2fa/enable", methods=["GET", "POST"])
@login_required
def enable_2fa():
    form = Enable2FAForm()

    # Confirmación (POST)
    if form.validate_on_submit():
        # Recuperar el secreto temporal de la sesión
        secret = session.get('totp_secret_pending')
        if not secret:
            flash("La sesión de configuración ha expirado. Inténtalo de nuevo.", "error")
            return redirect(url_for('profile.enable_2fa'))

        # Verificar que el token ingresado coincide con el secreto generado
        totp = pyotp.TOTP(secret)
        if totp.verify(form.verification_token.data):
            # Guardar el secreto permanentemente en el usuario
            current_user.totp_secret = secret
            db.session.commit()
            session.pop('totp_secret_pending', None) # Limpiar sesión
            flash("2FA activado correctamente.", "success")
            return redirect(url_for('profile.my_profile'))
        else:
            form.verification_token.errors.append("Código de verificación incorrecto.")

    # Generación y muestra del QR
    # Si no hay un secreto pendiente en sesión, generamos uno nuevo
    if 'totp_secret_pending' not in session:
        session['totp_secret_pending'] = pyotp.random_base32()

    secret = session['totp_secret_pending']

    # Generar el URI estándar para TOTP
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Dinosaur Hub"
    )

    # Generar la imagen QR en memoria
    qr_img = qrcode.make(totp_uri)
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    # Codifica en base64 para incrustarlo directamente en el HTML
    qr_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    qr_data_uri = f"data:image/png;base64,{qr_b64}"

    return render_template(
        "profile/enable_2fa.html",
        form=form,
        qr_data_uri=qr_data_uri,
        secret=secret
    )

@profile_bp.route("/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    # Ruta opcional para permitir al usuario desactivarlo
    current_user.totp_secret = None
    db.session.commit()
    flash("Autenticación de dos factores desactivada.", "info")
    return redirect(url_for('profile.my_profile'))
