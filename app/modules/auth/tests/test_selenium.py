import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def test_login_and_check_element():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f"{host}/login")

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)

        # Wait a little while to ensure that the action has been completed
        time.sleep(4)

        try:

            driver.find_element(By.XPATH, "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]")
            print("Test passed!")

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        # Close the browser
        close_driver(driver)


def test_login_user3_requires_2fa_and_accepts_valid_code():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Go to login and submit credentials for the 2FA-enabled user
        driver.get(f"{host}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        driver.find_element(By.NAME, "email").send_keys("user3@example.com")
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)

        # We should land on the 2FA page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "token"))
        )
        assert "/login/2fa" in driver.current_url

        # Enter the known valid test token and finish login
        token_field = driver.find_element(By.ID, "token")
        token_field.send_keys("123456")
        token_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]",
                )
            )
        )
    finally:
        close_driver(driver)


def test_login_user_without_2fa_goes_straight_home():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        driver.find_element(By.NAME, "email").send_keys("user1@example.com")
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)

        # Should not be redirected to the 2FA step
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]",
                )
            )
        )
        assert "/login/2fa" not in driver.current_url
    finally:
        close_driver(driver)


# Call the test function
test_login_and_check_element()
test_login_user3_requires_2fa_and_accepts_valid_code()
test_login_user_without_2fa_goes_straight_home()
