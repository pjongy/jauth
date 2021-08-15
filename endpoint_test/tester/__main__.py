import unittest

from endpoint_test.tester.test_user import TestUser

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    unittest.TextTestRunner(verbosity=2).run(suite)
