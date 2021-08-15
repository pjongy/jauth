import random
import unittest

from endpoint_test.tester import TEST_ENDPOINT
from endpoint_test.tester.util.request import post
from jauth.model.user import UserType


class TestUser(unittest.IsolatedAsyncioTestCase):
    async def test_email_user_signup_succeed(self):
        dummy_email = 'dummy@user.com'
        dummy_account = f'dummy{random.randint(0, 9999)}'
        dummy_password = 'dummy-password'
        status, body, _ = await post(f'{TEST_ENDPOINT}/users/email', parameters={
            'email': dummy_email,
            'account': dummy_account,
            'password': dummy_password,
            'extra': {},
        })
        assert status == 200
        user = body['result']
        assert user['email'] == dummy_email
        assert user['account'] == dummy_account
        assert user['type'] == UserType.EMAIL

    async def test_email_user_signup_failed_if_duplicated_account(self):
        dummy_email = 'dummy@user.com'
        dummy_account = f'dummy{random.randint(0, 9999)}'
        dummy_password = 'dummy-password'
        status, body, _ = await post(f'{TEST_ENDPOINT}/users/email', parameters={
            'email': dummy_email,
            'account': dummy_account,
            'password': dummy_password,
            'extra': {},
        })
        assert status == 200
        user = body['result']
        assert user['email'] == dummy_email
        assert user['account'] == dummy_account
        assert user['type'] == UserType.EMAIL

        status, body, _ = await post(f'{TEST_ENDPOINT}/users/email', parameters={
            'email': dummy_email,
            'account': dummy_account,
            'password': dummy_password,
            'extra': {},
        })
        assert status == 409
