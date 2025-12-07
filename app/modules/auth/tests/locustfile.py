import os

from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token

LOGIN_EMAIL = os.getenv("LOCUST_EMAIL", "user1@example.com")
LOGIN_PASSWORD = os.getenv("LOCUST_PASSWORD", "1234")
TWO_FA_CODE = os.getenv("LOCUST_2FA_CODE", "123456")  # FLASK_ENV=testing usa 123456


class SignupBehavior(TaskSet):
    def on_start(self):
        self.signup()

    @task
    def signup(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup", data={"email": fake.email(), "password": fake.password(), "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")


class LoginBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login",
            data={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD, "csrf_token": csrf_token},
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class TwoFactorLoginBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login_with_2fa()

    def ensure_logged_out(self):
        self.client.get("/logout", name="2fa_logout")

    @task
    def login_with_2fa(self):
        response = self.client.get("/login", name="2fa_login_page")
        if response.status_code != 200 or "Login" not in response.text:
            print("2FA: Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login", name="2fa_login_page_retry")

        csrf = get_csrf_token(response)

        # Primer paso: credenciales
        resp = self.client.post(
            "/login",
            data={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD, "csrf_token": csrf},
            name="2fa_login_submit",
            allow_redirects=True,
        )

        # Segundo paso: token 2FA (solo si se redirige)
        twofa_page = self.client.get("/login/2fa", name="2fa_page")
        if twofa_page.status_code == 200 and "Two-Factor" in twofa_page.text:
            twofa_csrf = get_csrf_token(twofa_page)
            self.client.post(
                "/login/2fa",
                data={"token": TWO_FA_CODE, "csrf_token": twofa_csrf},
                name="2fa_submit",
                allow_redirects=True,
            )


class AuthUser(HttpUser):
    tasks = [SignupBehavior, LoginBehavior, TwoFactorLoginBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
