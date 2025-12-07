import os
import re
import random

from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

LOGIN_EMAIL = os.getenv("LOCUST_EMAIL", "user1@example.com")
LOGIN_PASSWORD = os.getenv("LOCUST_PASSWORD", "1234")

VALID_CSV_PATH = os.path.abspath("app/modules/dataset/csv_examples/2023.csv")
if not os.path.exists(VALID_CSV_PATH):
    VALID_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../csv_examples/2023.csv"))


DATASET_ID = os.getenv("LOCUST_DATASET_ID","4")  
DATASET_DOI = os.getenv("LOCUST_DATASET_DOI","10.1234/dataset4")  


class DatasetBehavior(TaskSet):
    dataset_id = None
    dataset_doi = None
    csrf_token = None

    def on_start(self):
        self.login()
        self.pick_dataset()

    def login(self):
        resp = self.client.get("/login", name="login_page")
        self.csrf_token = get_csrf_token(resp)
        self.client.post(
            "/login",
            data={
                "email": LOGIN_EMAIL,
                "password": LOGIN_PASSWORD,
                "csrf_token": self.csrf_token,
            },
            name="login_submit",
            allow_redirects=True,
        )

    def pick_dataset(self):
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
    def upload_dataset_flow(self):
        upload_page_resp = self.client.get("/dataset/upload", name="dataset_upload_form")
        upload_csrf_token = get_csrf_token(upload_page_resp)
        if not upload_csrf_token:
            return

        if not os.path.exists(VALID_CSV_PATH):
            return 

        file_name = os.path.basename(VALID_CSV_PATH)
        with open(VALID_CSV_PATH, 'rb') as f:
            upload_resp = self.client.post(
                "/dataset/file/upload",
                files={"file": (file_name, f, "text/csv")},
                name="dataset_file_upload",
                headers={"X-CSRFToken": upload_csrf_token}
            )
        if upload_resp.status_code != 200:
            return

        form_data = {
            "title": f"Locust Test Dataset {random.randint(1000, 9999)}",
            "desc": "A dataset created during a load test.",
            "tags": "locust,test",
            "publication_doi": "",
            "dataset_doi": "",
            "authors-0-name": "Locust User",
            "authors-0-affiliation": "Testing Facility",
            "authors-0-orcid": "",
            "feature_models-0-uvl_filename": file_name,
            "feature_models-0-title": "Test Feature Model",
            "feature_models-0-desc": "",
            "feature_models-0-publication_doi": "",
            "feature_models-0-tags": "",
            "feature_models-0-version": "",
            "csrf_token": upload_csrf_token,
        }
        self.client.post(
            "/dataset/upload",
            data=form_data,
            name="dataset_upload_submit",
            headers={"X-CSRFToken": upload_csrf_token}
        )

        self.client.post(
            "/dataset/file/delete",
            json={"file": file_name}, name="dataset_file_delete"
        )

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

    @task
    def post_comment(self):
        dataset_id = self.dataset_id or DATASET_ID
        if not dataset_id:
            return

        self.client.post(
            f"/datasets/{dataset_id}/comments",
            data={"content": f"This is a test comment from locust {random.randint(1,100)}"},
            name="dataset_post_comment",
            allow_redirects=False 
        )


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
