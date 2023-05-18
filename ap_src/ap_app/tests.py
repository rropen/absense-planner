import pytest
from django.test import LiveServerTestCase
from seleniumbase import BaseCase

#TODO: Add id's to web-page elements being used during testing, instead of using xPaths 
#NOTE: 
# - If executing in terminal with pytest, must run command inside "ap_src" directory - (where "pytest.ini" is located)
# - Example in terminal: C:\[BASE_DIR]\ap_src> pytest
# main.yml does this automatically in CI pipeline. 

# LiveServerTestCase is used to run the django application on an alternative thread, while tests are being executed
# SB - Driver

# Consts 
DEMO = False



class TestBasicTemplate(LiveServerTestCase, BaseCase):
    """ Testing Suite Class - Implement any tests inside its own method - (Methods to be tests must start with "test_*") """

    # def setup(self, method=None):
    #     print(
    #         "[Test]: Running SeleniumBase Commands Now" \
    #         f"LiveServer running on: {self.live_server_url}"
    #         )
    #     if method:
    #         method()


    # Basic test examples
    def test_example_pass(self):
        # PASS expected
        self.demo_mode = DEMO
        self.headless = (DEMO is False)

        self.open(self.live_server_url)
        self.assert_true("Home" in self.get_page_title(), msg="[TESTING CODE ERROR]: Not on Home-Page - Title does not match")
        
            
    # def test_example_fail(self):
    #     # FAIL expected
    #     self.demo_mode = DEMO
    #     self.headless = (DEMO is False)

    #     self.open(self.live_server_url)
    #     self.assert_true("This is Not In Title" in self.get_page_title(), msg="[TESTING CODE ERROR]: Not on Home-Page - Title does not match")