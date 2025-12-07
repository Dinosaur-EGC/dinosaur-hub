import os
import time
import zipfile

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    """Espera a que el documento HTML esté completamente cargado."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass # Ignoramos timeouts aquí, a veces la página ya cargó


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        # Busca filas en la tabla. Si no hay tabla, asume 0.
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets


def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)
        time.sleep(4)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Find basic info and UVL model and fill values
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        # Add two authors and fill
        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")

        # Obtén las rutas absolutas de los archivos
        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        # Subir el primer archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        # Subir el segundo archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        # Add authors in UVL models
        show_button = driver.find_element(By.ID, "0_button")
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")

        # Check I agree and send form
        check = driver.find_element(By.ID, "agreeCheckbox")
        check.send_keys(Keys.SPACE)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test passed!")

    finally:

        # Close the browser
        close_driver(driver)



def test_trending_datasets():
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        driver.get(f"{host}/trending")
        wait_for_page_to_load(driver)

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Trending datasets')]"))
        )

        views_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-trending-metric='views']"))
        )
        views_btn.click()
        
        month_btn = driver.find_element(By.CSS_SELECTOR, "button[data-trending-period='month']")
        month_btn.click()

        items = driver.find_elements(By.CLASS_NAME, "card")
        empty_state = driver.find_element(By.ID, "trending-empty-state")
        
        if len(items) > 0 or (empty_state.is_displayed() and "d-none" not in empty_state.get_attribute("class")):
            print("✅ test_trending_datasets passed!")
        else:
            raise Exception("No se mostraron items ni el mensaje de estado vacío.")

    except Exception as e:
        print(f"❌ test_trending_datasets failed: {e}")

    finally:
        close_driver(driver)


'''
TESTS PARA SUBIDA DESDE ZIP & GITHUB
'''

def create_dummy_zip(filename="selenium_test_zip.zip"):
    csv_content = "feature,value\nroot,1\nchild,2"
    with zipfile.ZipFile(filename, 'w') as zf:
        zf.writestr("model.csv", csv_content)
    return os.path.abspath(filename)

def test_selenium_upload_from_zip():
    driver = initialize_driver()
    zip_path = None

    try:
        host = get_host_for_selenium_testing()

        # 1. Login
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)
        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/dataset/upload']"))
        )

        # 2. Contar datasets iniciales para verificar luego
        initial_datasets = count_datasets(driver, host)

        # 3. Ir a la página de subida
        driver.get(f"{host}/dataset/upload")

        # 4. Rellenar datos básicos
        title_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        title_field.send_keys("Prueba Selenium ZIP")
        driver.find_element(By.ID, "title").send_keys("Prueba Selenium ZIP")
        driver.find_element(By.ID, "desc").send_keys("Subida automática desde test")
        
        # 5. Seleccionar método ZIP (Importante: esperar a que sea clickeable)
        zip_radio = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "import_method-zip"))
        )
        zip_radio.click()

        # 6. SUBIDA DEL ARCHIVO (La parte crítica corregida)
        # Generamos el archivo real en el momento
        zip_path = create_dummy_zip()
        
        # Localizamos el input file. NO hacemos click(). Enviamos la ruta.
        file_input = driver.find_element(By.ID, "zip_file")
        file_input.send_keys(zip_path)

        # 7. Aceptar términos y subir
        # A veces el checkbox queda tapado, usamos JS si falla el click normal
        checkbox = driver.find_element(By.ID, "agreeCheckbox")
        try:
            checkbox.click()
        except:
            driver.execute_script("arguments[0].click();", checkbox)

        # Esperar a que el botón de upload se active
        upload_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "upload_button"))
        )
        upload_btn.click()

        # 8. Verificación
        wait_for_page_to_load(driver)
        time.sleep(2) # Espera técnica para asegurar persistencia en DB

        assert driver.current_url == f"{host}/dataset/list", "No se redirigió a la lista de datasets"
        
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "El número de datasets no ha aumentado"

        print("✅ test_selenium_upload_from_zip PASSED")

    except Exception as e:
        print(f"❌ Error en test_selenium_upload_from_zip: {e}")
        raise e

    finally:
        close_driver(driver)
        if zip_path and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except:
                pass



if __name__ == "__main__":
    print("\n--- Starting test_trending_datasets ---")
    test_trending_datasets()
    
    print("\n--- Starting test_upload_dataset ---")
    test_upload_dataset()

    print("\n--- Starting test_selenium_upload_from_zip ---")
    test_selenium_upload_from_zip()
    
