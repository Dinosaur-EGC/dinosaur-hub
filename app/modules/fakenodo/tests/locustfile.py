import io
from locust import HttpUser, task, between, SequentialTaskSet
from core.environment.host import get_host_for_locust_testing

class FakenodoBehavior(SequentialTaskSet):
    """
    Simula el ciclo de vida completo de un dataset en Fakenodo:
    Subida -> Listado -> Descarga -> Borrado.
    """
    
    current_dataset_id = None

    @task
    def upload_dataset(self):
        """
        Paso 1: Subir un archivo ficticio para generar un dataset.
        """
        # Creamos un archivo en memoria para no depender de archivos físicos
        file_content = b"Contenido de prueba generado por Locust para Fakenodo."
        files = {
            "file": ("locust_test_file.txt", file_content, "text/plain")
        }

        # Realizamos el POST a la ruta definida en routes.py
        with self.client.post("/fakenodo/upload", files=files, catch_response=True) as response:
            if response.status_code == 201:
                try:
                    # Guardamos el ID devuelto para usarlo en los siguientes pasos
                    self.current_dataset_id = response.json().get("id")
                    response.success()
                except Exception as e:
                    response.failure(f"Error parseando respuesta JSON: {e}")
            else:
                response.failure(f"Fallo en subida: {response.status_code}")

    @task
    def list_datasets(self):
        """
        Paso 2: Consultar la lista de todos los datasets.
        """
        self.client.get("/fakenodo/datasets")

    @task
    def get_dataset_info(self):
        """
        Paso 3: Intentar descargar/ver la info del dataset recién creado.
        """
        if self.current_dataset_id is not None:
            url = f"/fakenodo/info/{self.current_dataset_id}"
            
            with self.client.get(url, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    # Si falla por tipo de dato (str vs int) en el backend o no existe
                    response.failure("Dataset no encontrado (404)")
                else:
                    response.failure(f"Error al obtener info: {response.status_code}")

    @task
    def delete_dataset(self):
        """
        Paso 4: Borrar el dataset para limpiar.
        """
        if self.current_dataset_id is not None:
            url = f"/fakenodo/dataset/{self.current_dataset_id}"
            
            with self.client.delete(url, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                    self.current_dataset_id = None # Reseteamos el ID
                else:
                    response.failure(f"Fallo al borrar dataset: {response.status_code}")

class FakenodoUser(HttpUser):
    tasks = [FakenodoBehavior]
    wait_time = between(2, 5)
    host = get_host_for_locust_testing()
