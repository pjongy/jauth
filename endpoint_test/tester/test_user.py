import random
import unittest

from endpoint_test.tester import TEST_ENDPOINT
from endpoint_test.tester.util.request import post, get
from jauth.model.user import UserType


class TestUser(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        status, body, _ = await get(f"{TEST_ENDPOINT}/storage/clean-up")
        assert body["result"]["status"] == "done"

    async def test_email_user_signup_succeed(self):
        dummy_email = "dummy@user.com"
        dummy_account = f"dummy{random.randint(0, 9999)}"
        dummy_password = "dummy-password"
        status, body, _ = await post(
            f"{TEST_ENDPOINT}/users/email",
            parameters={
                "email": dummy_email,
                "account": dummy_account,
                "password": dummy_password,
                "extra": {},
            },
        )
        assert status == 200
        user = body["result"]
        assert user["email"] == dummy_email
        assert user["account"] == dummy_account
        assert user["type"] == UserType.EMAIL
        assert "third_party_user_id" not in user  # Only for third party users

    async def test_email_user_signup_failed_if_duplicated_account(self):
        dummy_email = "dummy@user.com"
        dummy_account = f"dummy{random.randint(0, 9999)}"
        dummy_password = "dummy-password"
        status, body, _ = await post(
            f"{TEST_ENDPOINT}/users/email",
            parameters={
                "email": dummy_email,
                "account": dummy_account,
                "password": dummy_password,
                "extra": {},
            },
        )
        assert status == 200
        user = body["result"]
        assert user["email"] == dummy_email
        assert user["account"] == dummy_account
        assert user["type"] == UserType.EMAIL

        status, body, _ = await post(
            f"{TEST_ENDPOINT}/users/email",
            parameters={
                "email": dummy_email,
                "account": dummy_account,
                "password": dummy_password,
                "extra": {},
            },
        )
        assert status == 409

    async def test_third_party_user_signup_succeed(self):
        # Tokens from /endpoint_test/jauth/application.py
        dummy_users = {
            "dummy-facebook-token": UserType.FACEBOOK,
            "dummy-kakao-token": UserType.KAKAO,
            "dummy-apple-token": UserType.APPLE,
            "dummy-google-token": UserType.GOOGLE,
        }
        for token, user_type in dummy_users.items():
            status, body, _ = await post(
                f"{TEST_ENDPOINT}/users/third_party",
                parameters={
                    "third_party_token": token,
                    "user_type": user_type,
                    "extra": {},
                },
            )
            assert status == 200
            user = body["result"]
            assert user["type"] == user_type
            assert "account" not in user  # Only for email users
            assert "third_party_user_id" in user

    async def test_third_party_user_signup_failed_if_duplicated_third_party_id(self):
        # Tokens from /endpoint_test/jauth/application.py
        dummy_users = {
            "dummy-facebook-token": UserType.FACEBOOK,
            "dummy-kakao-token": UserType.KAKAO,
            "dummy-apple-token": UserType.APPLE,
            "dummy-google-token": UserType.GOOGLE,
        }
        for token, user_type in dummy_users.items():
            status, body, _ = await post(
                f"{TEST_ENDPOINT}/users/third_party",
                parameters={
                    "third_party_token": token,
                    "user_type": user_type,
                    "extra": {},
                },
            )
            assert status == 200
            user = body["result"]
            assert user["type"] == user_type
            assert "account" not in user  # Only for email users
            assert "third_party_user_id" in user

        # Tokens from /endpoint_test/jauth/application.py
        dummy_users = {
            "dummy-facebook-token-dup": UserType.FACEBOOK,
            "dummy-kakao-token-dup": UserType.KAKAO,
            "dummy-apple-token-dup": UserType.APPLE,
            "dummy-google-token-dup": UserType.GOOGLE,
        }
        for token, user_type in dummy_users.items():
            status, body, _ = await post(
                f"{TEST_ENDPOINT}/users/third_party",
                parameters={
                    "third_party_token": token,
                    "user_type": user_type,
                    "extra": {},
                },
            )
            assert status == 409
