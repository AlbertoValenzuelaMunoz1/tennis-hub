import io
import zipfile

import pytest

from app.modules.hubfile.models import Hubfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_download_bulk_files_returns_zip(test_database_poblated):
    files = Hubfile.query.limit(2).all()
    assert len(files) == 2
    file_ids = [file.id for file in files]

    response = test_database_poblated.post(
        "/file/download/bulk",
        json={"file_ids": file_ids},
    )

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/zip")

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


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"
