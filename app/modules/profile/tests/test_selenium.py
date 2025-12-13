import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Importamos las funciones del core de tu proyecto
from core.selenium.common import close_driver, initialize_driver

# Configuración del Host (Usamos 5000 porque es el que sale en tu grabación)
try:
    from core.environment.host import get_host_for_selenium_testing
    HOST = get_host_for_selenium_testing()
except ImportError:
    HOST = "http://localhost:5000"

def login_user(driver):
    """
    Loguea al usuario 'user1' (creado por los seeders)
    """
    driver.get(f'{HOST}/login')
    # Esperamos un poco más por si el servidor va lento
    time.sleep(3)

    email_field = driver.find_element(By.ID, 'email')
    password_field = driver.find_element(By.ID, 'password')

    email_field.clear()
    email_field.send_keys('user1@example.com') 
    password_field.clear()
    password_field.send_keys('1234')
    
    # Usamos el botón submit por ID como en tu grabación
    driver.find_element(By.ID, "submit").click()
    time.sleep(3) # Esperar redirección al dashboard

def test_access_profile_summary():
    """Prueba que se puede entrar al perfil"""
    driver = initialize_driver()
    try:
        login_user(driver)
        
        # Navegación directa (más fiable que buscar en el sidebar)
        driver.get(f'{HOST}/profile/summary')
        time.sleep(2)

        if "User profile" in driver.page_source or "Summary" in driver.page_source:
            print('✅ Profile summary access test passed!')
        else:
            raise AssertionError('❌ Profile summary access test failed! Header not found.')

    finally:
        close_driver(driver)

def test_edit_profile_form():
    """Prueba la edición exitosa usando los datos de tu grabación"""
    driver = initialize_driver()
    try:
        login_user(driver)

        driver.get(f'{HOST}/profile/edit')
        time.sleep(2)

        # 1. Rellenar campos (Usando tus valores de la grabación)
        # Surname
        driver.find_element(By.ID, 'surname').clear()
        driver.find_element(By.ID, 'surname').send_keys('SeleniumUser')
        
        # Name
        driver.find_element(By.ID, 'name').clear()
        driver.find_element(By.ID, 'name').send_keys('TestingSel')
        
        # Affiliation
        driver.find_element(By.ID, 'affiliation').clear()
        driver.find_element(By.ID, 'affiliation').send_keys('Probando Test')

        # ORCID (Usando el que pusiste en la grabación)
        driver.find_element(By.ID, 'orcid').clear()
        driver.find_element(By.ID, 'orcid').send_keys('0000-0002-1825-0022')
        
        # 2. Enviar formulario
        driver.find_element(By.ID, "submit").click()
        
        # IMPORTANTE: Damos tiempo suficiente para que recargue la página
        time.sleep(4)

        # 3. Verificación
        try:
            # Buscamos la clase 'alert-success'
            success_alert = driver.find_element(By.CLASS_NAME, "alert-success")
            print(f"✅ Edit profile success test passed! Message: {success_alert.text.strip()}")
            
        except NoSuchElementException:
            # Si falla, imprimimos ayuda para depurar
            print("\n❌ DEBUG: No se encontró .alert-success. Buscando errores...")
            try:
                # Buscamos tu clase personalizada de error
                error_alert = driver.find_element(By.CLASS_NAME, "alert-error")
                print(f"   ⚠️ ERROR EN PANTALLA: '{error_alert.text.strip()}'")
            except NoSuchElementException:
                print("   ℹ️ No se encontró ninguna alerta (ni verde ni roja).")
                # Imprimimos el título de la página por si nos mandó a un error 500
                print(f"   Título de la página actual: {driver.title}")
            
            raise AssertionError("❌ Profile update failed.")

    finally:
        close_driver(driver)

def test_required_fields_validation():
    """Prueba de campos vacíos"""
    driver = initialize_driver()
    try:
        login_user(driver)
        driver.get(f'{HOST}/profile/edit')
        time.sleep(2)

        # Dejar nombre vacío
        driver.find_element(By.ID, 'name').clear()
        
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)

        # Si seguimos en la misma URL 'edit', es que la validación funcionó (no guardó)
        if "edit" in driver.current_url:
            print('✅ Required fields validation test passed!')
        else:
             raise AssertionError('❌ Validation failed: Form submitted with empty fields.')

    finally:
        close_driver(driver)

def test_invalid_orcid_format():
    """Prueba ORCID inválido"""
    driver = initialize_driver()
    try:
        login_user(driver)
        driver.get(f'{HOST}/profile/edit')
        time.sleep(2)

        driver.find_element(By.ID, 'orcid').clear()
        driver.find_element(By.ID, 'orcid').send_keys('bad-orcid-123')
        
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)

        # Verificamos si aparece tu alerta de error
        try:
            driver.find_element(By.CLASS_NAME, "alert-error")
            print('✅ ORCID validation test passed (alert-error found)!')
        except NoSuchElementException:
            # Fallback: buscar texto en la página
            src = driver.page_source
            if "Invalid ORCID" in src or "match the format" in src:
                print('✅ ORCID validation test passed (error text found)!')
            else:
                raise AssertionError('❌ ORCID validation test failed! No error message found.')

    finally:
        close_driver(driver)

if __name__ == "__main__":
    test_access_profile_summary()
    test_edit_profile_form()
    test_required_fields_validation()
    test_invalid_orcid_format()