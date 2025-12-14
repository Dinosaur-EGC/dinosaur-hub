from locust import HttpUser, task, between
from core.locust.common import get_csrf_token

class CartUser(HttpUser):
    wait_time = between(1,5)

    def on_start(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "test1234",
            "csrf_token": csrf_token
        })

    @task(4)
    def view_cart(self):
        self.client.get("/cart/")

    @task(4)
    def add_item_to_cart(self):
        hubfile_id = 1  
    
        response = self.client.get("/cart/")
        csrf_token = get_csrf_token(response)

        self.client.post(f"/cart/add/{hubfile_id}", headers={"X-CSRFToken": csrf_token})

    
    @task(2)
    def download_cart(self):
        self.client.get("/cart/download")
    
    @task(2)
    def empty_cart(self):
        response = self.client.get("/cart/")
        csrf_token = get_csrf_token(response)

        self.client.post("/cart/empty", json={}, headers={"X-CSRFToken": csrf_token})
