import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Importamos las funciones de tu entorno
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

def wait_for_page_to_load(driver, timeout=4):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass

def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)
    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets

def test_test2():
    # Inicialización del driver y host
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1. LOGIN
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        # Esperar login exitoso
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/dataset/upload']"))
        )

        initial_datasets = count_datasets(driver, host)

        # 2. IR A UPLOAD
        upload_url = f"{host}/dataset/upload"
        driver.get(upload_url)
        wait_for_page_to_load(driver)

        # 3. RELLENAR FORMULARIO PRINCIPAL
        title_field = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "title")))
        title_field.click()
        title_field.send_keys("test")

        driver.find_element(By.ID, "desc").send_keys("test")

        dropdown = driver.find_element(By.ID, "publication_type")
        dropdown.find_element(By.XPATH, "//option[. = 'Preprint']").click()
        
        # -----------------------------------------------------------------------
        # PARTE IMPORTADA DEL OTRO TEST: SUBIDA DE FICHERO EXISTENTE EN PROYECTO
        # -----------------------------------------------------------------------
        
        # 1. Usamos la ruta relativa del proyecto, igual que en test_upload_dataset
        file_path = os.path.abspath("app/modules/dataset/csv_examples/file1.csv")
        
        # 2. Localizamos el input oculto de Dropzone y enviamos el fichero
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file_path)

        # 3. Rellenamos los metadatos del fichero (Necesario si el otro test lo hacía)
        # Esperamos a que aparezca el botón para editar el fichero subido (id="0_button")
        show_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "0_button"))
        )
        show_button.click()

        # Rellenamos el título del fichero en el modal que se abre
        file_title_field = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "fossils_files-0-title"))
        )
        file_title_field.send_keys("CSV File Title Test")
        
        # -----------------------------------------------------------------------

        # Checkbox Agree
        agree_checkbox = driver.find_element(By.ID, "agreeCheckbox")
        driver.execute_script("arguments[0].click();", agree_checkbox)

        # Botón Upload (Forzado con JS para evitar errores de scroll)
        upload_btn = driver.find_element(By.ID, "upload_button")
        driver.execute_script("arguments[0].click();", upload_btn)

        # 4. VERIFICACIÓN ROBUSTA
        print("⏳ Esperando a que se complete la subida (timeout 20s)...")
        
        # Paso A: Esperar a que la URL cambie (éxito de subida)
        try:
            WebDriverWait(driver, 20).until(
                lambda driver: driver.current_url != upload_url
            )
        except Exception:
            print("⚠️ La URL no cambió. Comprobando errores...")
            try:
                # Imprimir errores en pantalla si los hay
                errors = driver.find_elements(By.CLASS_NAME, "invalid-feedback")
                for err in errors:
                    if err.is_displayed(): print(f"Error detectado: {err.text}")
            except: pass
            raise Exception("El formulario no se envió correctamente (Timeout).")

        # Paso B: Esperar carga de página destino
        wait_for_page_to_load(driver)

        # Paso C: Buscar el link "test"
        print("🔍 Buscando el enlace del nuevo dataset...")
        link_test = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "test"))
        )
        link_test.click()

        # Verificación final
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "El contador de datasets no aumentó."
        
        print("✅ test_test2 passed!")

    except Exception as e:
        print(f"❌ test_test2 failed en URL: {driver.current_url}")
        print(f"❌ Error: {e}")
        raise e

    finally:
        close_driver(driver)

if __name__ == "__main__":
    test_test2()