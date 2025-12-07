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

        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/dataset/upload']"))
        )

        initial_datasets = count_datasets(driver, host)

        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        driver.find_element(By.NAME, "title").send_keys("Title")
        driver.find_element(By.NAME, "desc").send_keys("Description")
        driver.find_element(By.NAME, "tags").send_keys("tag1,tag2")

        driver.find_element(By.ID, "add_author").click()
        driver.find_element(By.ID, "add_author").click()
        
        WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.NAME, "authors-0-name")))

        driver.find_element(By.NAME, "authors-0-name").send_keys("Author0")
        driver.find_element(By.NAME, "authors-0-affiliation").send_keys("Club0")
        driver.find_element(By.NAME, "authors-0-orcid").send_keys("0000-0000-0000-0000")

        driver.find_element(By.NAME, "authors-1-name").send_keys("Author1")
        driver.find_element(By.NAME, "authors-1-affiliation").send_keys("Club1")

        # Archivos CSV
        file1_path = os.path.abspath("app/modules/dataset/csv_examples/file1.csv")
        file2_path = os.path.abspath("app/modules/dataset/csv_examples/file2.csv")

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)

        show_button_0 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "0_button"))
        )
        show_button_0.click()

        title_field_0 = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "fossils_files-0-title"))
        )
        title_field_0.send_keys("CSV File 1 Title")
        driver.find_element(By.NAME, "fossils_files-0-description").send_keys("Description for CSV 1")

        show_button_1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "1_button"))
        )
        show_button_1.click()
        
        title_field_1 = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "fossils_files-1-title"))
        )
        title_field_1.send_keys("CSV File 2 Title")
        
        check = driver.find_element(By.ID, "agreeCheckbox")
        driver.execute_script("arguments[0].click();", check)

        upload_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "upload_button")))
        upload_btn.click()

        WebDriverWait(driver, 10).until(EC.url_to_be(f"{host}/dataset/list"))

        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"
        print("✅ test_upload_dataset passed!")

    finally:
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

        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)
        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        driver.find_element(By.NAME, "password").send_keys("1234")
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/dataset/upload']"))
        )

        initial_datasets = count_datasets(driver, host)

        driver.get(f"{host}/dataset/upload")

        title_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        title_field.send_keys("Prueba Selenium ZIP")
        driver.find_element(By.ID, "title").send_keys("Prueba Selenium ZIP")
        driver.find_element(By.ID, "desc").send_keys("Subida automática desde test")
        
        zip_radio = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "import_method-zip"))
        )
        zip_radio.click()

        zip_path = create_dummy_zip()
        
        file_input = driver.find_element(By.ID, "zip_file")
        file_input.send_keys(zip_path)

        checkbox = driver.find_element(By.ID, "agreeCheckbox")
        try:
            checkbox.click()
        except:
            driver.execute_script("arguments[0].click();", checkbox)

        upload_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "upload_button"))
        )
        upload_btn.click()

        wait_for_page_to_load(driver)
        time.sleep(2)

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
    
