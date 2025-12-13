from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token

class ProfileBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234",
            "csrf_token": csrf_token
        })

    @task(2)
    def view_profile_summary(self):
        self.client.get("/profile/summary")

    @task(1)
    def view_edit_profile(self):
        self.client.get("/profile/edit")

    @task(3)
    def edit_profile(self):
        response = self.client.get("/profile/edit")
        csrf_token = get_csrf_token(response)

        profile_data = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "orcid": "0000-0002-1825-0097",
            "affiliation": fake.company(),
            "csrf_token": csrf_token
        }

        self.client.post("/profile/edit", data=profile_data)

    # --- Tareas añadidas para perfiles ajenos ---
    @task(4)
    def view_other_user_profile(self):
        # Simular ver perfil de otro usuario (asumir ID aleatorio)
        user_id = fake.random_int(min=1, max=100)  # ID ficticio
        self.client.get(f"/profile/{user_id}")

    @task(2)
    def view_other_user_profile_with_datasets(self):
        # Simular perfil con datasets (asumir ID conocido con datasets)
        self.client.get("/profile/2")  # Asumir usuario con datasets

    @task(1)
    def view_nonexistent_user_profile(self):
        # Simular perfil inexistente para probar errores
        self.client.get("/profile/999")

class ProfileLoadTest(HttpUser):
    tasks = [ProfileBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()