import re
from locust import HttpUser, task, between, SequentialTaskSet
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token
from faker import Faker
import pyotp

# Usamos Faker para generar datos de usuario aleatorios
fake = Faker()

class TwoFactorAuthBehavior(SequentialTaskSet):
    """
    Define el comportamiento secuencial de un usuario probando el ciclo de vida del 2FA.
    """

    def on_start(self):
        # Se ejecuta al iniciar el usuario: generamos credenciales y nos registramos
        self.email = fake.email()
        self.password = fake.password()
        self.name = fake.first_name()
        self.surname = fake.last_name()
        self.totp_secret = None
        
        # Registramos al usuario (esto suele dejar al usuario logueado automáticamente)
        self.register()

    def register(self):
        # 1. Obtener página de registro para el CSRF
        res = self.client.get("/signup")
        if res.status_code != 200:
            print(f"Error al cargar signup: {res.status_code}")
            self.interrupt()
            return
            
        csrf_token = get_csrf_token(res)

        # 2. Enviar formulario de registro
        res = self.client.post("/signup", data={
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "surname": self.surname,
            "csrf_token": csrf_token
        })
        
        if res.status_code != 200:
            print(f"Fallo en el registro: {res.status_code}")
            self.interrupt()

    @task
    def enable_2fa(self):
        """Paso 1: Activar el 2FA desde el perfil"""
        # GET a la página de activación
        res = self.client.get("/2fa/enable")
        if res.status_code != 200:
            print(f"Error al acceder a /2fa/enable: {res.status_code}")
            return

        csrf_token = get_csrf_token(res)

        # Extraer el secreto TOTP del HTML usando Regex
        # Buscamos algo como: <strong>JBSWY3DPEHPK3PXP</strong>
        # Basado en tu template: 'introduce este código manualmente: <strong>{{ secret }}</strong>'
        match = re.search(r'<strong>([A-Z2-7=]+)</strong>', res.text)
        if match:
            self.totp_secret = match.group(1)
        else:
            print("No se pudo encontrar el secreto TOTP en la respuesta HTML.")
            self.interrupt()
            return

        # Generar el token actual usando el secreto extraído
        totp = pyotp.TOTP(self.totp_secret)
        current_token = totp.now()

        # Enviar el formulario de activación
        # En tu Enable2FAForm el campo es 'verification_token'
        res = self.client.post("/2fa/enable", data={
            "verification_token": current_token,
            "csrf_token": csrf_token
        })

        if "2FA activado correctamente" not in res.text and res.status_code != 200:
             print(f"Error al activar 2FA. Status: {res.status_code}")

    @task
    def logout(self):
        """Paso 2: Cerrar sesión para probar el login"""
        self.client.get("/logout")

    @task
    def login_full_flow(self):
        """Paso 3: Login completo con 2FA"""
        
        # --- Fase 1: Credenciales ---
        res = self.client.get("/login")
        csrf_token = get_csrf_token(res)

        res = self.client.post("/login", data={
            "email": self.email,
            "password": self.password,
            "csrf_token": csrf_token
        })

        # Verificamos si nos ha redirigido a la verificación de 2FA
        # Tu ruta es /login/verify-2fa
        if "/login/verify-2fa" in res.url or "verify-2fa" in res.text:
            
            # Necesitamos el CSRF de la nueva página de verificación
            # (A veces Locust sigue la redirección automáticamente y res ya es la página de 2fa)
            csrf_token_2fa = get_csrf_token(res)
            
            # Generamos un nuevo token
            if not self.totp_secret:
                print("Error: No tenemos secreto guardado para generar el token.")
                return

            totp = pyotp.TOTP(self.totp_secret)
            token_code = totp.now()

            # --- Fase 2: Verificación TOTP ---
            # En tu Verify2FAForm el campo es 'token'
            res = self.client.post("/login/verify-2fa", data={
                "token": token_code,
                "csrf_token": csrf_token_2fa
            })

            if res.status_code != 200:
                print(f"Fallo en la verificación 2FA: {res.status_code}")
        else:
            print("El login no redirigió a 2FA como se esperaba.")

    @task
    def disable_2fa(self):
        """Paso 4: Limpieza (Desactivar 2FA)"""
        # Para hacer el POST de desactivar, necesitamos un CSRF válido.
        # Lo cogemos del perfil mismo.
        res = self.client.get("/profile/summary")
        if res.status_code == 200:
            csrf_token = get_csrf_token(res)
            # La ruta en profile/routes.py es /2fa/disable (POST)
            self.client.post("/2fa/disable", data={"csrf_token": csrf_token})
        
        # Terminamos la secuencia para este usuario
        self.interrupt()

class TwoFactorUser(HttpUser):
    tasks = [TwoFactorAuthBehavior]
    wait_time = between(2, 5)
    host = get_host_for_locust_testing()