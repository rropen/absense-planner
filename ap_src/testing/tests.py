# Pip install seleniumbase on college laptops by doing - "python -m pip install selenium-base"
from seleniumbase import BaseCase

# Consts 
URL = "http://LocalHost:8000/"


class BasicTest(BaseCase):
    def test_basic(self):
        self.open(URL)
        self.assert_title("Home - RR Absence")
        self.click_xpath()