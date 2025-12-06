import os
import re

from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

LOGIN_EMAIL = os.getenv("LOCUST_EMAIL", "user1@example.com")
LOGIN_PASSWORD = os.getenv("LOCUST_PASSWORD", "1234")
DATASET_ID = os.getenv("LOCUST_DATASET_ID","4")  # optional fixed id
DATASET_DOI = os.getenv("LOCUST_DATASET_DOI","10.1234/dataset4")  # optional fixed doi


class DatasetBehavior(TaskSet):
    dataset_id = None
    dataset_doi = None

    def on_start(self):
        self.login()
        self.pick_dataset()

    def login(self):
        """Authenticate once per user to hit authenticated endpoints."""
        resp = self.client.get("/login", name="login_page")
        token = get_csrf_token(resp)
        self.client.post(
            "/login",
            data={
                "email": LOGIN_EMAIL,
                "password": LOGIN_PASSWORD,
                "csrf_token": token,
            },
            name="login_submit",
            allow_redirects=True,
        )

    def pick_dataset(self):
        """Grab a valid dataset id/doi from the list page to avoid 404s."""
        resp = self.client.get("/dataset/list", name="dataset_list_prefetch")
        if resp.status_code != 200:
            return

        id_match = re.search(r"/dataset/download/(\d+)", resp.text)
        if id_match:
            self.dataset_id = id_match.group(1)

        doi_match = re.search(r'href="[^"]*/doi/([^"]+)"', resp.text)
        if doi_match:
            self.dataset_doi = doi_match.group(1).strip("/")

    @task
    def upload_form(self):
        self.client.get("/dataset/upload", name="dataset_upload_form")

    @task(3)
    def list_datasets(self):
        self.client.get("/dataset/list", name="dataset_list")

    @task(2)
    def trending(self):
        self.client.get("/trending", name="dataset_trending")

    @task(2)
    def view_dataset(self):
        doi = DATASET_DOI
        if not doi:
            return
        self.client.get(f"/doi/{doi}/", name="dataset_view")

    @task
    def dataset_stats(self):
        dataset_id = self.dataset_id or DATASET_ID
        if not dataset_id:
            return
        self.client.get(f"/dataset/{dataset_id}/stats", name="dataset_stats")

    @task
    def download_dataset(self):
        dataset_id = self.dataset_id or DATASET_ID
        if not dataset_id:
            return
        self.client.get(f"/dataset/download/{dataset_id}", name="dataset_download")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
