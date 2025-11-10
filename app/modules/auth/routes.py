from flask import redirect, render_template, request, url_for, session, flash
from flask_login import current_user, login_user, logout_user

from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, SignupForm, Verify2FAForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f"Email {email} in use")

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f"Error creating user: {exc}")

        # Log user
        login_user(user, remember=True)
        return redirect(url_for("public.index"))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        # Buscamos al usuario por email sin loguearlo todavía.
        user = authentication_service.get_user_by_email(form.email.data)

        if user and user.check_password(form.password.data):
            # Comprobamos si el usuario tiene 2FA activado
            if user.totp_secret:
                # Guardamos temporalmente el ID del usuario y su preferencia de 'recordarme' en la sesión
                session['2fa_user_id'] = user.id
                session['2fa_remember'] = form.remember_me.data
                return redirect(url_for('auth.verify_2fa'))

            # Si NO tiene 2FA, procedemos con el login normal
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("public.index"))

        return render_template("auth/login_form.html", form=form, error="Credenciales inválidas")

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/login/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    # Si intentan acceder aquí sin haber pasado por el login primero, los echamos
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))

    form = Verify2FAForm()
    if form.validate_on_submit():
        # Recuperamos el usuario usando el ID guardado en sesión
        user = authentication_service.get_user_by_id(session['2fa_user_id'])

        # Verificamos el token TOTP
        if user and user.verify_totp(form.token.data):
            # Completamos el proceso de login.
            remember_me = session.get('2fa_remember', False)

            # Limpiamos las variables temporales de la sesión
            session.pop('2fa_user_id', None)
            session.pop('2fa_remember', None)

            login_user(user, remember=remember_me)
            return redirect(url_for('public.index'))
        else:
            flash("Código de autenticación inválido. Inténtalo de nuevo.", "danger")

    return render_template("auth/verify_2fa_form.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))
