import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def test_hubfile_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f"{host}/hubfile")

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        # Close the browser
        close_driver(driver)


def test_testcarritos():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(host)
        driver.set_window_size(1854, 1048)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Sample dataset 4"))
        ).click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(2) .add-to-cart",
        ).click()
        driver.find_element(By.ID, "carritoDropdown").click()
        driver.find_element(By.CSS_SELECTOR, ".fa-solid").click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(2) .add-to-cart",
        ).click()
        driver.find_element(By.ID, "carritoDropdown").click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(2) .add-to-cart",
        ).click()
        alert = driver.switch_to.alert
        assert alert.text == "Este archivo ya está en el carrito."

        # Cerramos el alert para poder seguir interactuando con la página
        alert.accept()
        driver.find_element(By.ID, "carritoDropdown").click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".flex-grow-1:nth-child(2)",
        ).click()
        driver.find_element(By.CSS_SELECTOR, ".content").click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(2) .add-to-cart",
        ).click()
        alert = driver.switch_to.alert
        assert alert.text == "Este archivo ya está en el carrito."
        alert.accept()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(3) .add-to-cart",
        ).click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".list-group-item:nth-child(4) .add-to-cart",
        ).click()
        driver.find_element(By.ID, "carritoDropdown").click()
        driver.find_element(
            By.CSS_SELECTOR,
            ".flex-grow-1:nth-child(1)",
        ).click()
    finally:
        # Close the browser
        close_driver(driver)


# Call the test function
test_hubfile_index()
test_testcarritos()
