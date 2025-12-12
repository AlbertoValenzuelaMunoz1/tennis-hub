import os
import random
import re

from bs4 import BeautifulSoup
from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

LOGIN_EMAIL = os.getenv("LOCUST_EMAIL", "user1@example.com")
LOGIN_PASSWORD = os.getenv("LOCUST_PASSWORD", "1234")

DATASET_ID = os.getenv("LOCUST_DATASET_ID", "4")
DATASET_DOI = os.getenv("LOCUST_DATASET_DOI", "10.1234/dataset4")

try:
    MIN_CART_ITEMS = max(1, int(os.getenv("LOCUST_CART_ITEMS", "2")))
except ValueError:
    MIN_CART_ITEMS = 2


class HubfileBehavior(TaskSet):
    dataset_id = None
    dataset_doi = None
    files = []

    def on_start(self):
        self.login()
        self.pick_dataset()
        self.refresh_files()

    def login(self):
        resp = self.client.get("/login", name="hubfile_login_page")
        csrf_token = get_csrf_token(resp)
        if not csrf_token:
            return
        self.client.post(
            "/login",
            data={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD, "csrf_token": csrf_token},
            name="hubfile_login_submit",
            allow_redirects=True,
        )

    def pick_dataset(self):
        resp = self.client.get("/dataset/list", name="hubfile_dataset_list")
        if resp.status_code != 200:
            return

        id_match = re.search(r"/dataset/download/(\d+)", resp.text)
        if id_match:
            self.dataset_id = id_match.group(1)

        doi_match = re.search(r'href="[^"]*/doi/([^"]+)"', resp.text)
        if doi_match:
            self.dataset_doi = doi_match.group(1).strip("/")

    def refresh_files(self):
        doi = self.dataset_doi or DATASET_DOI
        if not doi:
            return

        resp = self.client.get(f"/doi/{doi}/", name="hubfile_dataset_view")
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        files = []
        for button in soup.select(".add-to-cart"):
            file_id = button.get("data-id")
            if not file_id:
                continue
            files.append(
                {
                    "id": file_id,
                    "name": button.get("data-name") or "",
                    "size": button.get("data-size") or "",
                }
            )
        self.files = files

    def _pick_file(self):
        if not self.files:
            self.refresh_files()
        if not self.files:
            return None
        return random.choice(self.files)

    def _cart_file_ids(self):
        if not self.files:
            self.refresh_files()
        if not self.files:
            return []

        ids = []
        for file_info in self.files[:MIN_CART_ITEMS]:
            try:
                ids.append(int(file_info["id"]))
            except (TypeError, ValueError):
                continue
        return ids

    @task(3)
    def browse_dataset(self):
        self.refresh_files()

    @task(2)
    def download_single_file(self):
        file_info = self._pick_file()
        if not file_info:
            return

        file_id = file_info["id"]
        resp = self.client.get(f"/file/download/{file_id}", name="hubfile_file_download")
        if resp.status_code >= 400:
            resp.failure(f"Download failed for {file_id}: {resp.status_code}")

    @task(2)
    def view_file(self):
        file_info = self._pick_file()
        if not file_info:
            return

        file_id = file_info["id"]
        resp = self.client.get(f"/file/view/{file_id}", name="hubfile_file_view")
        if resp.status_code >= 400:
            resp.failure(f"View failed for {file_id}: {resp.status_code}")

    @task
    def download_cart(self):
        file_ids = self._cart_file_ids()
        if not file_ids:
            return

        resp = self.client.post(
            "/file/download/bulk",
            json={"file_ids": file_ids},
            name="hubfile_cart_download",
        )
        if resp.status_code >= 400:
            try:
                error = resp.json().get("error")
            except Exception:
                error = None
            resp.failure(f"Cart download failed ({resp.status_code}): {error or 'no error provided'}")

    @task
    def hubfile_index(self):
        self.client.get("/hubfile", name="hubfile_index")


class HubfileUser(HttpUser):
    tasks = [HubfileBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
