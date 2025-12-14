import re
import random
from locust import HttpUser, task, between, SequentialTaskSet
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

class FlamapyUserBehavior(SequentialTaskSet):
    """
    Simula el flujo de un usuario que navega por datasets y utiliza
    las herramientas de Flamapy sobre los archivos encontrados.
    """
    
    file_ids = []  # Almacenaremos los IDs de archivos UVL encontrados aquí

    def on_start(self):
        """
        Al iniciar, nos logueamos y buscamos archivos válidos en el sistema.
        """
        self.login()
        self.discover_csv_files()

    def login(self):
        """Logueo básico para tener acceso a los datasets."""
        response = self.client.get("/login")
        if response.status_code == 200:
            csrf_token = get_csrf_token(response)
            self.client.post("/login", data={
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token
            })

    def discover_csv_files(self):
        """
        Navega a la lista de datasets y entra en uno para buscar enlaces de Flamapy.
        Esto permite obtener IDs de archivos reales (file_id) para probar.
        """
        # 1. Obtener lista de datasets
        res = self.client.get("/dataset/list")
        if res.status_code != 200:
            print("Error al cargar la lista de datasets")
            return

        # Buscar enlaces a datasets (ej: /dataset/view/1)
        dataset_links = re.findall(r'href="(/dataset/view/\d+)"', res.text)
        
        if not dataset_links:
            print("No se encontraron datasets. Asegúrate de haber ejecutado los seeders.")
            return

        # 2. Entrar en un dataset aleatorio
        target_dataset = random.choice(dataset_links)
        res_ds = self.client.get(target_dataset)
        
        # 3. Buscar botones/enlaces de Flamapy para extraer IDs de archivos válidos
        # Buscamos patrones como: /flamapy/check_uvl/123
        # El grupo de captura (\d+) obtendrá el ID.
        found_ids = re.findall(r'/flamapy/check_uvl/(\d+)', res_ds.text)
        
        # Eliminamos duplicados y guardamos
        self.file_ids = list(set(found_ids))
        
        if not self.file_ids:
            print(f"No se encontraron archivos UVL en el dataset {target_dataset}")

    @task
    def test_flamapy_endpoints(self):
        """
        Prueba todos los endpoints definidos en routes.py usando los IDs recolectados.
        """
        if not self.file_ids:
            # Si no tenemos IDs, intentamos descubrirlos de nuevo (reintento)
            self.discover_csv_files()
            return

        # Seleccionamos un archivo al azar para probar
        file_id = random.choice(self.file_ids)
        
        # Definición de las rutas a probar (basado en tu routes.py)
        endpoints = [
            f"/flamapy/check_csv/{file_id}",
            f"/flamapy/valid/{file_id}",
            f"/flamapy/to_glencoe/{file_id}",
            f"/flamapy/to_splot/{file_id}",
            f"/flamapy/to_cnf/{file_id}"
        ]

        # Ejecutamos las peticiones
        for url in endpoints:
            with self.client.get(url, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 400 and "check_csv" in url:
                    # check_uvl puede devolver 400 si el modelo tiene errores de sintaxis,
                    # lo cual es una respuesta válida del servidor (no una caída).
                    response.success()
                else:
                    response.failure(f"Fallo en {url}: {response.status_code}")

class FlamapyUser(HttpUser):
    tasks = [FlamapyUserBehavior]
    # Espera entre 2 y 5 segundos entre tareas para simular lectura humana
    wait_time = between(2, 5)
    host = get_host_for_locust_testing()
