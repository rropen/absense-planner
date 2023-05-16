# Pip install seleniumbase on college laptops by doing - "python -m pip install selenium-base"
from seleniumbase import BaseCase

# Consts 
URL = "http://LocalHost:8000/"

# Hard-Coded temp values
USERNAME = "patrick"
PASSWORD = "password"

#NOTE: add id's instead of using xPaths

class BasicTest(BaseCase):
    def test_basic(self):
        self.open(URL)
        self.assert_title("Home - RR Absence")
        self.click_xpath("/html/body/container/div/container/div/a")

        # -=-= Login page =-=- 
        self.assert_true("Login" in self.get_page_title(), msg="[TESTING CODE ERROR]: Not on Login-Page")
        
        self.send_keys("/html/body/container/div/div/form/div[1]/div/input", text=USERNAME)
        self.send_keys("/html/body/container/div/div/form/div[2]/div/input", text=PASSWORD)
        # Click "Login"
        self.click_xpath("/html/body/container/div/div/form/button")


        if "Policy" in self.get_page_title():
            # -=-= Policy Page =-=-
            self.click_xpath("/html/body/container/div/div/form/input[2]")
            self.click_xpath("/html/body/container/div/div/form/button")
        
        # -=-= Main Calendar Page =-=-

        self.click_xpath("/html/body/nav/div[2]/div[1]/a[3]")

        # -=-= Teams Page =-=-


        self.wait(8)