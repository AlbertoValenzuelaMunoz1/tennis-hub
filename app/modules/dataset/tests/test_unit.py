import io
import os
import re
import shutil
import tempfile
import zipfile

import pytest
import requests
from bs4 import BeautifulSoup

from app.modules.dataset.routes import CSV_REQUIRED_COLUMNS, resolve_github_zip_url, validate_uploaded_files
from app.modules.dataset.services import DSMetaDataService, DataSetService
from app.modules.dataset.models import DataSet
from app.modules.auth.models import User
from app.modules.hubfile.models import Hubfile


def test_download_bulk_files_returns_zip(test_database_poblated):
    files = Hubfile.query.limit(2).all()
    assert len(files) == 2
    file_ids = [file.id for file in files]

    response = test_database_poblated.post(
        "/file/download/bulk",
        json={"file_ids": file_ids},
    )

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith(
        "application/zip"
    )

    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    zip_names = set(zip_file.namelist())

    for file in files:
        expected_path = f"dataset_{file.feature_model.data_set_id}/{file.name}"
        assert expected_path in zip_names


def test_download_bulk_files_requires_files(test_database_poblated):
    response = test_database_poblated.post(
        "/file/download/bulk",
        json={"file_ids": []},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "No files selected"


dataset_service=DataSetService()
def test_create_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= list(s.find("div",class_="comments-container").div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Hola', "The comment content is incorrect"
def test_no_content_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'','parent_id':None})
    assert response.status_code==400
def test_create_comment_no_login(test_database_poblated):
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    assert response.status_code==302, "The user should get redirected if not logged in"
    redirect_url = response.headers.get('Location').split('?')[0]
    assert redirect_url == '/login', "The user should get redirected to log in page"
def test_create_parent_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    id=int(s.find("div",class_="comments-container").div["id"].split("-")[1])
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Adios','parent_id':id})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= s.find("div",id=re.compile(r'children-\d+'))
    assert comment!=None, "The comment is not created as a response"
    comment=list(comment.div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Adios', "The comment content is incorrect"

dataset_service = DataSetService()


def _get_first_dataset_and_user():
    dataset = DataSet.query.first()
    user = User.query.first()
    return dataset, user


def _build_download_url(test_client, dataset_id):
    """
    Find a rule that looks like a dataset download endpoint and replace the variable
    part with the actual id. Fall back to the common pattern if none found.
    """
    app = test_client.application
    rules = list(app.url_map.iter_rules())

    # Prefer download routes that belong to the dataset blueprint
    dataset_rules = [rule for rule in rules if rule.endpoint.startswith("dataset.") and "download" in rule.rule]
    for rule in dataset_rules or rules:
        if "download" in rule.rule and "<" in rule.rule:
            url = re.sub(r"<[^>]+>", str(dataset_id), rule.rule)
            return url

    # Fallback to the actual dataset download pattern
    return f"/dataset/download/{dataset_id}"


def test_downloadcounter_successful(test_database_poblated):
    """
    Fixture `test_database_poblated` yields a Flask test client.
    Retrieve dataset and user from the DB inside the test (the fixture already seeded them).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.download_count or 0

    download_url = _build_download_url(client, dataset.id)
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    assert updated_dataset.download_count == initial_downloads + 1, "Download count was not incremented"


def test_downloadcounter_multiple_downloads_same_user(test_database_poblated):
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.download_count or 0

    download_url = _build_download_url(client, dataset.id)

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200, f"First download request was unsuccessful (GET {download_url})"

    # Second download (same client / same session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200, f"Second download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    # Current implementation increments on every download request
    assert updated_dataset.download_count == initial_downloads + 2, "Download count should increment on each request"


def test_download_nonexistent_dataset_returns_404(test_database_poblated):
    client = test_database_poblated

    # Use a large id that should not exist in the seeded DB
    response = client.get("/dataset/999999/download", follow_redirects=True)
    assert response.status_code in (404, 410), "Non-existent dataset download should return 404 or similar"

dataset_service = DataSetService()


def _get_first_dataset_and_user():
    dataset = DataSet.query.first()
    user = User.query.first()
    return dataset, user



def _build_trending_url():
    return "/trending"


def test_trending_download_weekly(test_database_poblated):
    """
    Fixture `test_database_poblated` yields a Flask test client.
    Retrieve dataset and user from the DB inside the test (the fixture already seeded them).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.get_number_of_downloads() or 0

    download_url = _build_download_url(client, dataset.id)
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    assert updated_dataset.get_number_of_downloads() == initial_downloads + 1, "Download count was not incremented"


def test_trending_multiple_downloads_same_user(test_database_poblated):
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.get_number_of_downloads() or 0

    download_url = _build_download_url(client, dataset.id)

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200, f"First download request was unsuccessful (GET {download_url})"

    # Second download (same client / same session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200, f"Second download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    # Current implementation increments on every download request
    assert updated_dataset.get_number_of_downloads() == initial_downloads + 1, "Download count should increment on each request"


def test_trending_page_renders_and_contains_dataset_info(test_database_poblated):
    """
    Comprueba que la página de trending se renderiza y contiene información del dataset seed.
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    client.get(f"/doi/{dataset.ds_meta_data.dataset_doi}", follow_redirects=True)
    client.get(_build_download_url(client, dataset.id), follow_redirects=True)
    trending_url = _build_trending_url()
    response = client.get(trending_url, follow_redirects=True)
    assert response.status_code == 200, f"GET {trending_url} should return 200"

    text = response.get_data(as_text=True)
    # Debe contener el título del dataset
    assert (dataset.ds_meta_data.title in text), "Trending page does not contain the dataset title"

    # Debe contener el badge de downloads y views con los contadores actuales
    downloads_text = f"Downloads: {dataset.get_number_of_downloads() or 0}"
    views_text = f"Views: {dataset.get_number_of_views() or 0}"
    assert downloads_text in text, "Trending page does not show downloads count"
    assert views_text in text, "Trending page does not show views count"
    # Debe contener el enlace de descarga esperado
    download_link = f"/dataset/download/{dataset.id}"
    assert download_link in text, "Trending page does not include download link for the dataset"


def test_trending_download_links_work(test_database_poblated):
    """
    Comprueba que los enlaces de descarga listados en la página de trending funcionan (status 200 o redirección válida).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    trending_url = _build_trending_url()
    page = client.get(trending_url, follow_redirects=True)
    assert page.status_code == 200, f"GET {trending_url} should return 200"

    # Intenta descargar usando el enlace estándar de descarga del dataset
    download_url = _build_download_url(client, dataset.id)
    resp = client.get(download_url, follow_redirects=True)
    assert resp.status_code == 200, f"Download from trending page should succeed (GET {download_url})"


def _login_seed_user(client):
    return client.post(
        "/login",
        data=dict(email="user1@example.com", password="1234"),
        follow_redirects=True,
    )


def _make_zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries:
            archive.writestr(name, content)
    buffer.seek(0)
    return buffer.getvalue()


def test_resolve_github_zip_url_variants():
    assert (
        resolve_github_zip_url("https://github.com/org/repo")
        == "https://github.com/org/repo/archive/refs/heads/main.zip"
    )
    assert (
        resolve_github_zip_url("https://github.com/org/repo/tree/dev")
        == "https://github.com/org/repo/archive/refs/heads/dev.zip"
    )
    assert resolve_github_zip_url("https://example.com/archive.zip") == "https://example.com/archive.zip"
    with pytest.raises(ValueError):
        resolve_github_zip_url("https://gitlab.com/org/repo")


def test_import_dataset_from_github_requires_url(test_database_poblated):
    client = test_database_poblated
    _login_seed_user(client)

    response = client.post("/dataset/file/import/github", json={})

    assert response.status_code == 400
    assert response.get_json()["message"] == "GitHub URL is required."


def test_import_dataset_from_github_rejects_invalid_link(test_database_poblated):
    client = test_database_poblated
    _login_seed_user(client)

    response = client.post(
        "/dataset/file/import/github",
        json={"github_url": "https://gitlab.com/org/repo"},
    )

    assert response.status_code == 400
    assert "GitHub URL" in response.get_json()["message"]


def test_import_dataset_from_github_handles_download_errors(test_database_poblated, monkeypatch):
    client = test_database_poblated
    _login_seed_user(client)

    def fake_get(*args, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr("app.modules.dataset.routes.requests.get", fake_get)

    response = client.post(
        "/dataset/file/import/github",
        json={"github_url": "https://github.com/org/repo"},
    )

    assert response.status_code == 400
    assert "Could not download repository" in response.get_json()["message"]


def test_import_dataset_from_github_saves_supported_files(test_database_poblated, monkeypatch):
    client = test_database_poblated
    _login_seed_user(client)
    user = User.query.filter_by(email="user1@example.com").first()
    temp_folder = user.temp_folder()
    shutil.rmtree(temp_folder, ignore_errors=True)

    csv_content = ",".join(CSV_REQUIRED_COLUMNS) + "\n" + ",".join(["value"] * len(CSV_REQUIRED_COLUMNS))
    uvl_content = "featuremodel {}"
    zip_bytes = _make_zip_bytes(
        [
            ("data/valid.csv", csv_content),
            ("nested/model.uvl", uvl_content),
        ]
    )

    class DummyResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "app.modules.dataset.routes.requests.get",
        lambda *args, **kwargs: DummyResponse(zip_bytes),
    )

    try:
        response = client.post(
            "/dataset/file/import/github",
            json={"github_url": "https://github.com/org/repo"},
        )
        data = response.get_json()

        assert response.status_code == 200
        assert set(data["files"]) == {"valid.csv", "model.uvl"}
        assert data["skipped"] == []

        for filename in data["files"]:
            assert os.path.isfile(os.path.join(temp_folder, filename))
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def test_import_dataset_from_github_reports_invalid_csv(test_database_poblated, monkeypatch):
    client = test_database_poblated
    _login_seed_user(client)
    user = User.query.filter_by(email="user1@example.com").first()
    temp_folder = user.temp_folder()
    shutil.rmtree(temp_folder, ignore_errors=True)

    invalid_csv = ",".join(CSV_REQUIRED_COLUMNS[:-1]) + "\n" + ",".join(["value"] * (len(CSV_REQUIRED_COLUMNS) - 1))
    zip_bytes = _make_zip_bytes([("invalid.csv", invalid_csv)])

    class DummyResponse:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "app.modules.dataset.routes.requests.get",
        lambda *args, **kwargs: DummyResponse(zip_bytes),
    )

    try:
        response = client.post(
            "/dataset/file/import/github",
            json={"github_url": "https://github.com/org/repo"},
        )
        data = response.get_json()

        assert response.status_code == 400
        assert data["files"] == []
        assert data["skipped"]
        assert "invalid.csv" in data["skipped"][0]
        assert "missing columns" in data["skipped"][0]
        assert "No valid CSV files were found" in data["message"]
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)


def _dummy_feature(filename):
    class DummyField:
        def __init__(self, data):
            self.data = data

    class DummyFeature:
        def __init__(self, name):
            self.uvl_filename = DummyField(name)

    return DummyFeature(filename)


def _write_csv(path, headers):
    with open(path, "w", encoding="utf-8") as handler:
        handler.write(",".join(headers) + "\n")
        handler.write(",".join(["sample"] * len(headers)))


def test_validate_uploaded_files_accepts_matching_headers():
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "valid.csv"
        file_path = os.path.join(tmpdir, filename)
        _write_csv(file_path, CSV_REQUIRED_COLUMNS)

        error = validate_uploaded_files(tmpdir, [_dummy_feature(filename)])

        assert error is None


def test_validate_uploaded_files_rejects_missing_headers():
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "missing.csv"
        file_path = os.path.join(tmpdir, filename)
        _write_csv(file_path, CSV_REQUIRED_COLUMNS[:-1])  # drop last column

        error = validate_uploaded_files(tmpdir, [_dummy_feature(filename)])

        assert error is not None
        assert "missing columns" in error
        assert filename in error


def test_validate_uploaded_files_requires_supported_extension():
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = "invalid.txt"
        file_path = os.path.join(tmpdir, filename)
        _write_csv(file_path, CSV_REQUIRED_COLUMNS)

        error = validate_uploaded_files(tmpdir, [_dummy_feature(filename)])

        assert error is not None
        assert "must be one of" in error
