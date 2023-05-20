import pytest
from django.test import LiveServerTestCase
from seleniumbase import BaseCase

#TODO: Add id's to web-page elements being used during testing, instead of using xPaths 
#NOTE: 
# Method of executing tests locally from command-line:
# C:\[BASE_DIR]> pytest --cov=ap_app ap_src/ap_app
# Before running tests make sure you have pip installed:
# - pytest-cov
# - pytest-django
# Useful Pytest arguments:
# - specifying "--headless" SB will NOT open a browser during tests 
# - specifying "--disable-warnings" pytest will hide all warnings
# main.yml does this all automatically in CI Testing pipeline. 

# LiveServerTestCase - Used to run the django application on an alternative thread, while tests are being executed
# BaseCase - Driver

# Consts 
# Activating "DEMO" will tell selenium to simulate the UI actions during testing
DEMO = True


class TestSuiteTemplate(LiveServerTestCase, BaseCase):
    """ Testing Suite Class - Implement any tests inside
    its own method - (Methods to be tests must start with "test_*") """
    
# Basic test examples
    def test_example_pass(self):
        self.demo_mode = DEMO

        # PASS expected
        self.open(self.live_server_url)
        self.assert_true("Home" in self.get_page_title(),
            msg="[ERROR]: Not on Home-Page - Title does not match")
        
    

    # def test_example_fail(self):
    #     self.demo_mode = DEMO

    #     # FAIL expected
    #     self.open(self.live_server_url)
    #     self.assert_true("This is Not In Title" in self.get_page_title(),
    #         msg="[ERROR]: Not on Home-Page - Title does not match")
        