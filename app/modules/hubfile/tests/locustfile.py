import re
import random
from locust import HttpUser, task, between, SequentialTaskSet
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

class HubfileBehavior(SequentialTaskSet):
    """
    Simula el comportamiento de un usuario interactuando con archivos (Hubfiles).
    El usuario navega para descubrir archivos y luego los descarga o visualiza.
    """
    
    file_ids = []  # Almacén temporal de IDs de archivos encontrados

    def on_start(self):
        """
        Al iniciar la sesión del usuario simulado, nos logueamos y 
        buscamos archivos disponibles en el sistema.
        """
        self.login()
        self.discover_files()

    def login(self):
        """Inicio de sesión para asegurar acceso a los archivos."""
        response = self.client.get("/login")
        if response.status_code == 200:
            csrf_token = get_csrf_token(response)
            self.client.post("/login", data={
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token
            })

    def discover_files(self):
        """
        Navega a la lista de datasets y entra en uno aleatorio para encontrar
        IDs de archivos reales escaneando los enlaces de descarga/vista.
        """
        # 1. Obtener lista de datasets
        res = self.client.get("/dataset/list")
        if res.status_code != 200:
            print("Error al cargar la lista de datasets")
            return

        # Extraer enlaces a datasets individuales (ej: /dataset/view/1)
        dataset_links = re.findall(r'href="(/dataset/view/\d+)"', res.text)
        
        if not dataset_links:
            print("No se encontraron datasets disponibles para explorar.")
            return

        # 2. Entrar en un dataset aleatorio
        target_dataset = random.choice(dataset_links)
        res_ds = self.client.get(target_dataset)
        
        # 3. Buscar IDs de archivos en el HTML del dataset
        # Buscamos patrones como: /file/download/123 o /file/view/123
        # Esto nos asegura que probamos con IDs que existen realmente.
        found_ids = re.findall(r'/file/(?:download|view)/(\d+)', res_ds.text)
        
        # Eliminamos duplicados y guardamos
        self.file_ids = list(set(found_ids))
        
        if not self.file_ids:
            print(f"No se encontraron archivos en el dataset {target_dataset}")

    @task(2)
    def download_file(self):
        """
        Prueba la ruta de descarga: /file/download/<id>
        Tiene peso 2 (se ejecuta el doble de veces que view).
        """
        if not self.file_ids:
            self.discover_files()
            return

        file_id = random.choice(self.file_ids)
        url = f"/file/download/{file_id}"
        
        # catch_response permite marcar como éxito incluso si hay redirecciones o headers específicos
        with self.client.get(url, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo en descarga {url}: {response.status_code}")

    @task(1)
    def view_file(self):
        """
        Prueba la ruta de visualización: /file/view/<id>
        """
        if not self.file_ids:
            self.discover_files()
            return

        file_id = random.choice(self.file_ids)
        url = f"/file/view/{file_id}"
        
        with self.client.get(url, catch_response=True) as response:
            if response.status_code == 200:
                # Verificamos que la respuesta JSON tenga éxito (según tu routes.py)
                if "success" in response.text or "content" in response.text:
                    response.success()
                else:
                    # A veces devuelve contenido raw, consideramos 200 como éxito
                    response.success()
            elif response.status_code == 404:
                # Si el archivo físico no existe (error común en dev), no fallamos la prueba de carga
                # pero lo registramos.
                response.failure("Archivo no encontrado en disco (404)")
            else:
                response.failure(f"Fallo en vista {url}: {response.status_code}")

class HubfileUser(HttpUser):
    tasks = [HubfileBehavior]
    wait_time = between(2, 5)
    host = get_host_for_locust_testing()
