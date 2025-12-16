import os
import shutil
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

USER1_EMAIL = os.getenv("SELENIUM_LOGIN_EMAIL", "user1@example.com")
USER1_PASSWORD = os.getenv("SELENIUM_LOGIN_PASSWORD", "1234")


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState")
        == "complete"
    )


def get_user_id_by_email(email: str):
    """Lookup the user id in the database so tests do not rely on seeded ids."""
    from app import app
    from app.modules.auth.models import User

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            raise RuntimeError(f"User with email {email} not found in the database")
        return user.id


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(
            driver.find_elements(By.XPATH, "//table//tbody//tr")
        )
    except Exception:
        amount_datasets = 0
    return amount_datasets

def remove_temp_folder(user_id):
    temp_folder = os.path.join(os.getenv("UPLOADS_DIR", "uploads"), "temp", str(user_id))
    shutil.rmtree(temp_folder, ignore_errors=True)


def _login_and_open_github_import(driver):
    host = get_host_for_selenium_testing()
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    password_field = driver.find_element(By.NAME, "password")
    email_field.clear()
    email_field.send_keys(USER1_EMAIL)
    password_field.clear()
    password_field.send_keys(USER1_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(4)

    driver.get(f"{host}/dataset/import/github")
    wait_for_page_to_load(driver)


def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys(USER1_EMAIL)
        password_field.send_keys(USER1_PASSWORD)

        # Send the form
        password_field.send_keys(Keys.RETURN)
        time.sleep(4)
        wait_for_page_to_load(driver)

        # Count initial datasets
        initial_datasets = count_datasets(driver, host)

        # Open the upload dataset
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        # Find basic info and UVL model and fill values
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        # Add two authors and fill
        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(
            By.NAME,
            "authors-0-affiliation",
        )
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(
            By.NAME,
            "authors-0-orcid",
        )
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(
            By.NAME,
            "authors-1-affiliation",
        )
        affiliation_field1.send_keys("Club1")

        # Obtén las rutas absolutas de los archivos
        file1_path = os.path.abspath(
            "app/modules/dataset/csv_examples/2023.csv"
        )
        file2_path = os.path.abspath(
            "app/modules/dataset/csv_examples/2022.csv"
        )

        # Subir el primer archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file1_path)
        wait_for_page_to_load(driver)

        # Subir el segundo archivo
        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(file2_path)
        wait_for_page_to_load(driver)

        # Add authors in UVL models
        show_button = driver.find_element(By.ID, "0_button")
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(
            By.ID, "0_form_authors_button"
        )
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(
            By.NAME,
            "feature_models-0-authors-2-name",
        )
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(
            By.NAME,
            "feature_models-0-authors-2-affiliation",
        )
        affiliation_field.send_keys("Club3")

        # Check I agree and send form
        check = driver.find_element(By.ID, "agreeCheckbox")
        check.send_keys(Keys.SPACE)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        # Count final datasets
        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test passed!")

    finally:
        # Close the browser
        close_driver(driver)
        


def _login_user1(driver, host):
    """Log in as user1 to reuse across dataset upload scenarios."""
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)
    driver.find_element(By.NAME, "email").send_keys(USER1_EMAIL)
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(USER1_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]")
        )
    )


def _login_and_open_dataset(driver, host, dataset_link_text="Sample dataset 1"):
    """Authenticate and navigate to a dataset detail page by its link text."""
    _login_user1(driver, host)
    link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, dataset_link_text))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, dataset_link_text)))
    try:
        link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", link)
    wait_for_page_to_load(driver)


def _fill_basic_dataset_fields(driver, host, file_path, title="CSV validation test"):
    driver.get(f"{host}/dataset/upload")
    wait_for_page_to_load(driver)

    driver.find_element(By.NAME, "title").send_keys(title)
    driver.find_element(By.NAME, "desc").send_keys("Description")
    driver.find_element(By.NAME, "tags").send_keys("tag1,tag2")

    dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
    dropzone.send_keys(file_path)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//ul[@id='file-list']//h4[contains(text(), '{os.path.basename(file_path)}')]")
        )
    )
    # Agree to terms so the upload button activates
    driver.find_element(By.ID, "agreeCheckbox").send_keys(Keys.SPACE)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "upload_button"))
    )


def test_upload_dataset_with_invalid_csv_headers_shows_error():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        _login_user1(driver, host)

        invalid_file = os.path.abspath(
            "app/modules/dataset/csv_examples/invalid_missing_columns.csv"
        )
        _fill_basic_dataset_fields(driver, host, invalid_file, title="Invalid headers")

        driver.find_element(By.ID, "upload_button").click()

        # The server should reject the dataset and surface the error on screen
        error_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "upload_error"))
        )
        assert "missing columns" in error_box.text or "must include the columns" in error_box.text
    finally:
        try:
            remove_temp_folder(get_user_id_by_email(USER1_EMAIL))
        finally:
            close_driver(driver)


def test_upload_dataset_with_valid_csv_succeeds():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        _login_user1(driver, host)

        valid_file = os.path.abspath(
            "app/modules/dataset/csv_examples/2023.csv"
        )
        _fill_basic_dataset_fields(driver, host, valid_file, title="Valid CSV upload")

        driver.find_element(By.ID, "upload_button").click()

        WebDriverWait(driver, 15).until(
            EC.url_contains("/dataset/list")
        )
        assert "/dataset/list" in driver.current_url
    finally:
        close_driver(driver)


def test_rejects_non_csv_extension_client_side():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        _login_user1(driver, host)

        bad_file = os.path.abspath(
            "app/modules/dataset/csv_examples/not_csv.txt"
        )
        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        dropzone.send_keys(bad_file)

        alert_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "alerts"))
        )
        assert "Invalid file extension" in alert_box.text
    finally:
        close_driver(driver)

def test_testdownloadcounter():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}")
        driver.set_window_size(602, 743)
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.LINK_TEXT, "Sample dataset 4")
        )
        ).click()
        descargas = int(driver.find_element(By.ID, "downloads-badge").text.split(": ")[1])
        driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        driver.get(driver.current_url)
        descargas2 = int(driver.find_element(By.ID, "downloads-badge").text.split(": ")[1])
        assert descargas2 == descargas + 1
    finally:
        # Close the browser
        close_driver(driver)
        

def test_comentarios():
    driver = initialize_driver()
    host = get_host_for_selenium_testing()


    driver.get(host + "/")

    # Ir al dataset de prueba
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.LINK_TEXT, "Sample dataset 4")
        )
        ).click()

    # Iniciar sesión
    driver.get(host+"/login")
    driver.find_element(By.ID, "email").send_keys(USER1_EMAIL)
    driver.find_element(By.ID, "password").send_keys(USER1_PASSWORD)
    driver.find_element(By.ID, "submit").click()

    # Volver al dataset
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.LINK_TEXT, "Sample dataset 4")
        )
        ).click()

    # Crear primer comentario
    driver.find_element(By.NAME, "content").send_keys("Hola")
    driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(3)").click()

    # Esperar a que aparezca el comentario “Hola”
    hola_comment = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'comment') and contains(., 'Hola')]")
        )
    )
    assert hola_comment is not None, "No se encontró el comentario con texto 'Hola'"

    # Click en “Reply” (buscar el span dentro del comentario que contenga “Reply”)
    reply_button = hola_comment.find_element(By.XPATH, ".//span[contains(text(), 'Reply')]")
    reply_button.click()

    # Escribir la respuesta
    driver.find_element(By.NAME, "content").send_keys("Adios")
    driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(3)").click()

    adios_comment = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((
        By.XPATH,
        "//div[contains(@id, 'children')]/div[contains(@class, 'comment') and contains(., 'Adios')]"
    ))
)

    assert adios_comment is not None, "No se encontró el comentario con texto 'Adios'"
    assert adios_comment.value_of_css_property("margin-left") =="20px"

    driver.quit()

def test_import_github_requires_url_feedback():
    driver = initialize_driver()

    try:
        _login_and_open_github_import(driver)

        github_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "github_import_btn"))
        )
        github_btn.click()

        feedback = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "import_feedback"))
        )
        assert "GitHub" in feedback.text
    finally:
        close_driver(driver)


def test_import_github_rejects_non_github_link():
    driver = initialize_driver()

    try:
        _login_and_open_github_import(driver)

        github_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "github_url"))
        )
        github_input.clear()
        github_input.send_keys("https://gitlab.com/org/repo")
        driver.find_element(By.ID, "github_import_btn").click()

        feedback = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "import_feedback"))
        )
        text = feedback.text.lower()
        assert "github" in text and "valid" in text
    finally:
        close_driver(driver)

def test_testImportarBien():
    driver = initialize_driver()
    host = get_host_for_selenium_testing()
    
    try:
        driver.get(host)
        driver.set_window_size(602, 743)
        driver.get(host+"/login")
        driver.find_element(By.ID, "email").click()
        driver.find_element(By.ID, "email").send_keys(USER1_EMAIL)
        driver.find_element(By.ID, "password").click()
        driver.find_element(By.ID, "password").send_keys(USER1_PASSWORD)
        driver.find_element(By.ID, "submit").click()
        time.sleep(2)
        driver.get(host+"/dataset/import/github")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "github_url")
            )
            ).click()
        driver.find_element(By.ID, "github_url").send_keys("https://github.com/AlbertoValenzuelaMunoz1/test-repository-tennis-hub")
        driver.find_element(By.ID, "github_import_btn").click()
        
        
    finally:
        try:
            remove_temp_folder(get_user_id_by_email(USER1_EMAIL))
        finally:
            close_driver(driver)
def test_user_datasets():



    driver = initialize_driver()





    try:


        host=get_host_for_selenium_testing()


        driver.get(host)


        driver.set_window_size(2174, 1368)


        WebDriverWait(driver, 10).until(


            EC.presence_of_element_located(


                (By.LINK_TEXT, "Sample dataset 4")


            )


            ).click()


        WebDriverWait(driver, 10).until(


            EC.presence_of_element_located(


                (By.LINK_TEXT, "Doe, Jane")


            )


            ).click()


        datasets=WebDriverWait(driver, 10).until(


            EC.presence_of_element_located(


                (By.CLASS_NAME,"card-body")


            )


            ).text


        assert  "Sample dataset 2" in datasets


        assert  "Sample dataset 4" in datasets


    finally:


        close_driver(driver)


# Call the test function
test_upload_dataset()
test_upload_dataset_with_invalid_csv_headers_shows_error()
test_upload_dataset_with_valid_csv_succeeds()
test_rejects_non_csv_extension_client_side()
test_testdownloadcounter()
test_comentarios()
test_testImportarBien()
test_import_github_requires_url_feedback()
test_import_github_rejects_non_github_link()
test_user_datasets()