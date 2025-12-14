import time
import re
import pyotp
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

def test_full_2fa_flow():
    driver = initialize_driver()
    
    timestamp = int(time.time())
    user_email = f"test_2fa_{timestamp}@example.com"
    user_pass = "password123"

    try:
        host = get_host_for_selenium_testing()
        print(f"Iniciando test 2FA en: {host}")

        # ---------------------------------------------------------
        # PASO 1: REGISTRO (Signup)
        # ---------------------------------------------------------
        print("Paso 1: Registrando usuario...")
        driver.get(f"{host}/signup")
        time.sleep(2)

        driver.find_element(By.NAME, "name").send_keys("Test")
        driver.find_element(By.NAME, "surname").send_keys("Selenium")
        driver.find_element(By.NAME, "email").send_keys(user_email)
        driver.find_element(By.NAME, "password").send_keys(user_pass)
        driver.find_element(By.NAME, "submit").click()
        time.sleep(3)

        # ---------------------------------------------------------
        # PASO 2: ACTIVAR 2FA (Enable)
        # ---------------------------------------------------------
        print("Paso 2: Activando 2FA...")
        driver.get(f"{host}/2fa/enable")
        time.sleep(2)

        page_source = driver.page_source
        match = re.search(r'manualmente: <strong>([A-Z2-7=]+)</strong>', page_source)
        
        if not match:
            raise AssertionError("No se pudo encontrar el secreto TOTP en la pantalla.")
        
        secret = match.group(1)
        print(f"   Secreto encontrado: {secret}")

        totp = pyotp.TOTP(secret)
        code = totp.now()

        input_verify = driver.find_element(By.NAME, "verification_token")
        input_verify.send_keys(code)
        input_verify.send_keys(Keys.RETURN)
        time.sleep(3)

        if "2FA activado correctamente" not in driver.page_source and "/profile/summary" not in driver.current_url:
             raise AssertionError("Fallo al activar el 2FA")

        # ---------------------------------------------------------
        # PASO 3: LOGOUT
        # ---------------------------------------------------------
        print("Paso 3: Cerrando sesión...")
        driver.get(f"{host}/logout")
        time.sleep(2)

        # ---------------------------------------------------------
        # PASO 4: LOGIN CON 2FA
        # ---------------------------------------------------------
        print("Paso 4: Intentando Login con 2FA...")
        driver.get(f"{host}/login")
        time.sleep(2)

        driver.find_element(By.NAME, "email").send_keys(user_email)
        driver.find_element(By.NAME, "password").send_keys(user_pass)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(2)

        if "verify-2fa" not in driver.current_url:
            raise AssertionError("El login no redirigió a la verificación de 2FA.")

        new_code = totp.now()
        
        token_field = driver.find_element(By.NAME, "token")
        token_field.send_keys(new_code)
        token_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # ---------------------------------------------------------
        # VERIFICACIÓN FINAL
        # ---------------------------------------------------------
        try:
            driver.find_element(By.XPATH, "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]")
            print("¡Test 2FA COMPLETADO EXITOSAMENTE!")

        except NoSuchElementException:
            print("Error: No se encontró la página de inicio tras el 2FA.")
            print(f"URL actual: {driver.current_url}")
            raise AssertionError("Login 2FA fallido.")

    except Exception as e:
        print(f"Test falló con excepción: {e}")
        raise e

    finally:
        close_driver(driver)

if __name__ == "__main__":
    test_full_2fa_flow()