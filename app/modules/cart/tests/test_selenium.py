import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

def wait_for_page_to_load(driver, timeout=4):
  try: 
    WebDriverWait(driver, timeout).until(
      lambda d: d.execute_script('return document.readyState') == 'complete'
    )
  except Exception:
    pass

def clean_cart(driver, host):
  print(" Verificando si el carrito tiene elementos para limpiar...")
  driver.get(f"{host}/cart/")
  wait_for_page_to_load(driver)

  if "Your cart is empty" not in driver.page_source:
    try:
      empty_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#emptyCartModal']")
      empty_btn.click()
      time.sleep(1)

      confirm_btn = driver.find_element(By.CSS_SELECTOR, "#emptyCartModal button[type='submit']")
      confirm_btn.click()
      
      WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element(
          (By.TAG_NAME, "body"), "Cart emptied successfully"
        )
      )
      print(" Carrito limpiado con éxito.")
    except Exception as e:
      print(f"Error al limpiar el carrito: {e}")
  
  else:
    print(" El carrito ya está vacío.")

def add_files_from_current_dataset(driver, amount=2):
  print(f"Intentando añadir {amount} archivos al carrito desde el dataset actual")

  add_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='cart_button_']")

  if len(add_buttons) < amount:
    print(f"Solo se encontraron {len(add_buttons)} archivos para añadir al carrito.")
    amount = len(add_buttons)
  
  count = 0
  for button in add_buttons[:amount]:
    driver.execute_script("arguments[0].scrollIntoView();", button)
    time.sleep(1)

    if "Added"  in button.text:
      print("El archivo ya está en el carrito, saltando...")
    else:
      button.click()
      WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element(
          (By.ID, button.get_attribute('id')), "Added"
        )
      )
      print(f"Archivo añadido al carrito (botón ID: {button.get_attribute('id')})")
      count += 1  
  return count
    

def test_cart_features():
  driver = initialize_driver()
  try:
    host = get_host_for_selenium_testing()
    print(f"\nEjecutando test de Carrito en: {host}")

    #1: LOGIN
    print("Paso 1: Login")
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)

    driver.find_element(By.NAME, "email").send_keys("user1@example.com")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.ID, "submit").click()

    wait_for_page_to_load(driver)

    assert "Log out" in driver.page_source, "Fallo al hacer Login"

    #1.5: LIMPIEZA INICIAL
    clean_cart(driver, host)

    #2: IR LISTA DE DATASETS
    print("Paso 2: Identificar datasets")
    driver.get(f"{host}/")
    
    dataset_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/dataset/'], a[href*='/doi/']")

    unique_urls = []

    for linlk in dataset_links:
      url = linlk.get_attribute("href")
      if url and url not in unique_urls and "download" not in url and "upload" not in url and "list" not in url: 
        unique_urls.append(url) 

    print(f"Se encontraron {len(unique_urls)} datasets únicos.")
    if len(unique_urls) < 2:
      raise Exception("No hay suficientes datasets para realizar la prueba.")

    #2.1: PROCESAR PRIMER DATASET
    print(f"Paso 2.1: Procesar primer dataset: {unique_urls[0]}")
    driver.get(unique_urls[0])
    wait_for_page_to_load(driver)

    added_ds1 = add_files_from_current_dataset(driver, amount=2)

    #2.2: PROCESAR SEGUNDO DATASET
    print(f"Paso 2.2: Procesar segundo dataset: {unique_urls[1]}")
    driver.get(unique_urls[1])
    wait_for_page_to_load(driver)

    added_ds2 = add_files_from_current_dataset(driver, amount=2)

    total_expected = added_ds1 + added_ds2
    print(f"Total de archivos añadidos al carrito: {total_expected}")


    #3: VERIFICAR CARRITO
    print("Paso 3: Verificar carrito")
    driver.find_element(By.CSS_SELECTOR, ".feather-shopping-cart").click()
    wait_for_page_to_load(driver)

    remove_buttons = driver.find_elements(By.CSS_SELECTOR, "button[title='Remove']")
    print(f"Archivos encontrados en el carrito: {len(remove_buttons)}")

    assert len(remove_buttons) == total_expected, f"Se esperaban {total_expected} archivos en el carrito, pero se encontraron {len(remove_buttons)}."

    print("El número de archivos en el carrito es correcto.")

    #4: BORRAR UN ITEM
    print("Paso 4: Borrar un item del carrito")
    if len(remove_buttons) > 0:
      remove_buttons[0].click()
      WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Item removed successfully")
      )
      print("Item eliminado correctamente.")

    #5: DESCARGAR CARRITO
    print("Paso 5: Descargar carrito")
    if "Your cart is empty" not in driver.page_source:
      driver.find_element(By.PARTIAL_LINK_TEXT, "Download Models").click()
      time.sleep(3)  # Esperar a que inicie la descarga
      assert "Internal Server Error" not in driver.page_source, "Error al descargar el carrito"
      print("Descarga del carrito iniciada correctamente.")

    #6: VACIAR CARRITO (Limpieza final)
    print("Paso 6: Vaciar carrito")
    clean_cart(driver, host)

    print("TEST SELENIUM COMPLETO CON ÉXITO.")
    


  except Exception as e:
    print(f"Error durante la prueba del carrito: {e}")
    driver.save_screenshot("error_selenium_cart.png")
    raise e
  finally:
    close_driver(driver)

if __name__ == "__main__":
  test_cart_features()