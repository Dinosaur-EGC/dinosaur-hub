from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

# --- Comportamiento Existente (Subida de Datasets) ---
class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()

# --- NUEVO Comportamiento (Trending Datasets) ---
class TrendingBehavior(TaskSet):
    """
    Simula usuarios consultando los datasets en tendencia con distintos filtros.
    """
    
    @task(3)
    def get_trending_default(self):
        # Petición por defecto (más frecuente)
        self.client.get("/datasets/trending")

    @task(2)
    def get_trending_views_month(self):
        # Cambio de filtros: vistas por mes
        self.client.get("/datasets/trending?metric=views&period=month")

    @task(1)
    def get_trending_custom_limit(self):
        # Filtro de límite personalizado
        self.client.get("/datasets/trending?metric=downloads&period=week&limit=5")

class TrendingUser(HttpUser):
    # Asignamos el comportamiento definido arriba
    tasks = [TrendingBehavior]
    # Tiempos de espera ligeramente menores para simular navegación rápida en listas
    min_wait = 1000 
    max_wait = 5000 
    host = get_host_for_locust_testing()