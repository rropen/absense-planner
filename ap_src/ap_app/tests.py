import pytest
from django.test import LiveServerTestCase
from seleniumbase import SB

#TODO: Add id's to web-page elements being used during testing, instead of using xPaths 
#NOTE: 
# - If executing in terminal with pytest, must run command inside "ap_src" directory - (where "pytest.ini" is located)
# - Example in terminal: C:\[BASE_DIR]\ap_src> pytest
# main.yml does this automatically in CI pipeline. 

# LiveServerTestCase is used to run the django application on an alternative thread, while tests are being executed
# SB - Driver

# Consts 
DEMO = False
#change

class TestBasicTemplate(LiveServerTestCase):
    def test_example(self):
        print(
            "[Application]: Running SeleniumBase Commands Now" \
            f"LiveServer running on: {self.live_server_url}"
            )

        with SB(demo=DEMO, headless=(DEMO is False)) as sb:
            sb.open(self.live_server_url)
            
            # Basic test examples
            # PASS expected
            sb.assert_true("Home" in sb.get_page_title(), msg="[TESTING CODE ERROR]: Not on Home-Page - Title does not match")   
            # FAIL expected
           # sb.assert_true("This is not in title" in sb.get_page_title(), msg="[TESTING CODE ERROR]: Not on Home-Page - Title does not match") 