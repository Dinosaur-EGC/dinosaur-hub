import io
import zipfile
from locust import HttpUser, task, between
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

class DatasetUser(HttpUser):
    wait_time = between(1, 5)
    host = get_host_for_locust_testing()

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

    def create_dummy_zip(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('model.csv', 'header1,header2\nval1,val2')
        buffer.seek(0)
        return buffer

    @task(1)
    def upload_from_zip(self):
        response = self.client.get("/dataset/upload")
        csrf_token = get_csrf_token(response)

        zip_buffer = self.create_dummy_zip()

        data = {
            "title": "Load Test ZIP Dataset",
            "desc": "Description for load test zip upload",
            "publication_type": "none",
            "tags": "test,locust,zip",
            "import_method": "zip",
            "csrf_token": csrf_token
        }

        files = {
            "zip_file": ("test_upload.zip", zip_buffer, "application/zip")
        }

        self.client.post("/dataset/upload", data=data, files=files)

    @task(1)
    def upload_from_github(self):
        response = self.client.get("/dataset/upload")
        csrf_token = get_csrf_token(response)

        data = {
            "title": "Load Test GitHub Dataset",
            "desc": "Description for load test github upload",
            "publication_type": "none",
            "tags": "test,locust,github",
            "import_method": "github",
            "github_url": "https://github.com/sbf6606/csv-files",
            "csrf_token": csrf_token
        }

        self.client.post("/dataset/upload", data=data)