"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

class SimpleTest(TestCase):
    # def setUp (self):
    #     """
    #     Set things up.
    #     """
    #     create_test_data.do_it_all ()

    def test_basic (self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)
        c = Client ()
        test_url_list = ['/erp_test/home/login/',
                         '/erp_test/home/login',
                         '/erp_test/home/',
                         '/erp_test/home',
                         '/erp_test/',
                         '/erp_test',
                         '/erp_test/h',
                         '/erp_test/home/',
                         '/erp_test/home',
                         '/erp_test/home/login/',
                         '/erp_test/home/login',
                         '/erp_test/home/forgot_password',
                         '/erp_test/home/forgot_password/',
                         '/erp_test/home/logout',
                         '/erp_test/home/logout/',
                         '/erp_test/ee09b001/users',
                         '/erp_test/ee09b001/users/',
                         '/erp_test/ee09b001/users/register/',
                         '/erp_test/ee09b001/users/register',
                         '/erp_test/ee09b001/users/register/new',
                         '/erp_test/ee09b001/users/invite/',
                         '/erp_test/ee09b001/users/edit_profile/',
                         ]
        for url in test_url_list:
            response = c.get (url)
            try:
                print url, response.status_code
            except:
                pass

# class AnimalTestCase(unittest.TestCase):
#     def setUp(self):
#         self.lion = Animal.objects.create(name="lion", sound="roar")
#         self.cat = Animal.objects.create(name="cat", sound="meow")

#     def testSpeaking(self):
#         self.assertEqual(self.lion.speak(), 'The lion says "roar"')
#         self.assertEqual(self.cat.speak(), 'The cat says "meow"')

# __test__ = {"doctest": """
# Another way to test that 1 + 1 is equal to 2.

# >>> 1 + 1 == 2
# True
# """}

