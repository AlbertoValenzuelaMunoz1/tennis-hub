import pytest
import pyotp
from flask import url_for, session

from app.modules.auth.repositories import UserRepository
from app.modules.auth.services import AuthenticationService
from app.modules.profile.repositories import UserProfileRepository


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        auth_service = AuthenticationService()
        if not auth_service.is_email_available("test@example.com"):
            # User already exists from a previous test run or global setup
            pass
        else:
            auth_service.create_with_profile(
                name="Test", surname="User", email="test@example.com", password="test1234"
            )

    yield test_client


# @pytest.fixture(scope="function")
# def test_client_with_user_2fa(test_client, clean_database):
#     """Fixture to create a user with 2FA enabled for testing."""
#     with test_client.application.app_context():
#         auth_service = AuthenticationService()
#         user = auth_service.create_with_profile(name="2FA", surname="User", email="2fa_user@example.com", password="test1234")
#         user.has_2fa_enabled = True
#         user.otp_secret = pyotp.random_base32() # Ensure a fresh secret for each test
#         auth_service.repository.session.commit()
#     yield user, test_client

def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"


def test_service_create_with_profie_success(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "service_test@example.com", "password": "test1234"}

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "", "password": "1234"}

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_login_with_2fa_redirects_to_2fa_page(test_database_poblated):
    response = test_database_poblated.post(
        "/login", data=dict(email="user3@example.com", password="1234"), follow_redirects=False
    )
    assert response.status_code == 302
    assert response.location == url_for("auth.login_2fa")


def test_login_2fa_with_valid_token(test_database_poblated):
    response = test_database_poblated.post(
        "/login", data=dict(email="user3@example.com", password="1234"), follow_redirects=False
    )
    response = test_database_poblated.post(
        url_for("auth.login_2fa"), data=dict(token="123456"), follow_redirects=True
    )

    assert response.request.path == "/"


def test_login_2fa_with_invalid_token(test_database_poblated):
    response = test_database_poblated.post(
        "/login", data=dict(email="user3@example.com", password="1234"), follow_redirects=False
    )
    response = test_database_poblated.post(
        url_for("auth.login_2fa"), data=dict(token="654321"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login_2fa")


def test_enable_2fa_flow(test_database_poblated):
    test_database_poblated.post("/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True)

    response = test_database_poblated.get(url_for("auth.enable_2fa"))
    assert b"Enable Two-Factor Authentication" in response.data

    response = test_database_poblated.post(url_for("auth.enable_2fa"), follow_redirects=True)
    assert response.request.path == url_for("auth.verify_2fa")

    # Verify and enable 2FA
    response = test_database_poblated.post(url_for("auth.verify_2fa"), data=dict(token="123456"), follow_redirects=True)
    assert response.request.path == url_for("profile.edit_profile")
    assert b"Two-factor authentication has been enabled!" in response.data

    test_database_poblated.get("/logout", follow_redirects=True)
    assert UserRepository().get_by_email("user1@example.com").has_2fa_enabled == 1

def test_enable_2fa_flow_invalid_token(test_database_poblated):
    test_database_poblated.post("/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True)

    response = test_database_poblated.get(url_for("auth.enable_2fa"))
    assert b"Enable Two-Factor Authentication" in response.data

    response = test_database_poblated.post(url_for("auth.enable_2fa"), follow_redirects=True)
    assert response.request.path == url_for("auth.verify_2fa")

    response = test_database_poblated.post(url_for("auth.verify_2fa"), data=dict(token="654321"), follow_redirects=True)
    assert response.request.path == url_for("auth.verify_2fa")

    test_database_poblated.get("/logout", follow_redirects=True)
    assert UserRepository().get_by_email("user1@example.com").has_2fa_enabled == 0

def test_disable_2fa(test_database_poblated):

    test_database_poblated.post("/login", data=dict(email="user3@example.com", password="1234"))
    test_database_poblated.post(url_for("auth.login_2fa"), data=dict(token="123456"), follow_redirects=True)


    response = test_database_poblated.post(
        url_for("auth.disable_2fa"), data=dict(token="123456"), follow_redirects=True
    )
    assert response.request.path == url_for("profile.edit_profile")
    assert b"Two-factor authentication has been disabled." in response.data
    assert UserRepository().get_by_email("user3@example.com").has_2fa_enabled == 0

def test_disable_2fa_invalid_token(test_database_poblated):

    test_database_poblated.post("/login", data=dict(email="user3@example.com", password="1234"))
    test_database_poblated.post(url_for("auth.login_2fa"), data=dict(token="123456"), follow_redirects=True)


    response = test_database_poblated.post(
        url_for("auth.disable_2fa"), data=dict(token="654321"), follow_redirects=True
    )
    assert response.request.path == url_for("profile.edit_profile")
    assert UserRepository().get_by_email("user3@example.com").has_2fa_enabled == 1


def test_service_create_with_profile_fail_no_password(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "test@example.com", "password": ""}

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0
