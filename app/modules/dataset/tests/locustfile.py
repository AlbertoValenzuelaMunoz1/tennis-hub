import os
import re
import random

from bs4 import BeautifulSoup
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
COMMENT_DELETE_PATH = os.getenv(
    "LOCUST_COMMENT_DELETE_PATH",
    "/datasets/{dataset_id}/comments/{comment_id}/delete",
)
COMMENT_RESOLVE_PATH = os.getenv(
    "LOCUST_COMMENT_RESOLVE_PATH",
    "/datasets/{dataset_id}/comments/{comment_id}/resolve",
)
COMMENT_DELETE_METHOD = os.getenv("LOCUST_COMMENT_DELETE_METHOD", "POST").upper()
COMMENT_RESOLVE_METHOD = os.getenv("LOCUST_COMMENT_RESOLVE_METHOD", "POST").upper()


class DatasetBehavior(TaskSet):
    dataset_id = None
    dataset_doi = None
    csrf_token = None


def _extract_user_datasets_url(self, html):


    soup = BeautifulSoup(html, "html.parser")





    # Busca enlaces que vayan a /user/<id>/datasets


    for a in soup.find_all("a", href=True):


        if re.match(r"/user/\d+/datasets", a["href"]):


            return a["href"]

        return None

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

    def _build_comment_action_path(self, template, dataset_id, comment_id):
        try:
            return template.format(dataset_id=dataset_id, comment_id=comment_id)
        except Exception:
            return None

    @staticmethod
    def _extract_comment_id(html, content_marker):
        soup = BeautifulSoup(html, "html.parser")
        for comment_div in soup.select("div.comment[id^='comment-']"):
            body_text = " ".join(comment_div.stripped_strings)
            if content_marker in body_text:
                match = re.search(r"comment-(\d+)", comment_div.get("id", ""))
                if match:
                    return match.group(1)
        return None

    def _create_comment_for_moderation(self):
        dataset_id = self.dataset_id or DATASET_ID
        doi = self.dataset_doi or DATASET_DOI
        if not dataset_id:
            return None, None

        marker = f"Locust moderation {random.randint(1_000, 9_999)}"
        resp = self.client.post(
            f"/datasets/{dataset_id}/comments",
            data={"content": marker},
            name="dataset_post_comment_moderation",
            allow_redirects=False,
        )
        if resp.status_code not in (200, 201, 302):
            return dataset_id, None

        view_url = resp.headers.get("Location")
        if not view_url and doi:
            view_url = f"/doi/{doi}/"

        if not view_url:
            return dataset_id, None

        view_resp = self.client.get(view_url, name="dataset_comment_lookup")
        if view_resp.status_code != 200:
            return dataset_id, None

        comment_id = self._extract_comment_id(view_resp.text, marker)
        return dataset_id, comment_id

    @task
    def delete_comment(self):
        dataset_id, comment_id = self._create_comment_for_moderation()
        if not dataset_id or not comment_id:
            return

        path = self._build_comment_action_path(COMMENT_DELETE_PATH, dataset_id, comment_id)
        if not path:
            return

        payload = {"dataset_id": dataset_id, "comment_id": comment_id}
        request_method = self.client.delete if COMMENT_DELETE_METHOD == "DELETE" else self.client.post

        with request_method(path, json=payload, name="dataset_comment_delete", catch_response=True) as resp:
            if resp.status_code >= 400:
                resp.failure(f"Failed to delete comment {comment_id}: {resp.status_code}")

    @task
    def resolve_comment(self):
        dataset_id, comment_id = self._create_comment_for_moderation()
        if not dataset_id or not comment_id:
            return

        path = self._build_comment_action_path(COMMENT_RESOLVE_PATH, dataset_id, comment_id)
        if not path:
            return

        payload = {"dataset_id": dataset_id, "comment_id": comment_id, "resolved": True}
        request_method = self.client.patch if COMMENT_RESOLVE_METHOD == "PATCH" else self.client.post

        with request_method(path, json=payload, name="dataset_comment_resolve", catch_response=True) as resp:
            if resp.status_code >= 400:
                resp.failure(f"Failed to resolve comment {comment_id}: {resp.status_code}")

    @task(2)
    def user_dataset(self):

        doi = DATASET_DOI

        if not doi:

            return

        resp = self.client.get(f"/doi/{doi}/", name="dataset_view")


        if resp.status_code != 200:


            return

        user_url = self._extract_user_datasets_url(resp.text)


        if not user_url:


            return


        self.client.get(user_url, name="user_datasets")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
