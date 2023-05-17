from django.test import LiveServerTestCase
# Pip install seleniumbase - "python -m pip install selenium-base"
#from seleniumbase import Driver
from seleniumbase import SB
import pytest

# Consts 
URL = "http://LocalHost:8000"

# Hard-Coded temp values
USERNAME = "patrick"
PASSWORD = "password"

#NOTE: add id's instead of using xPaths


DEMO = False


class HostTest(LiveServerTestCase):
    def test_basic(self):
        print("[Application]: Running SeleniumBase Commands Now")
        print(self.live_server_url)
        with SB(demo=DEMO, headless=(DEMO is False)) as sb:
            
            sb.open(self.live_server_url)
            print("Home-page title is: " + sb.get_page_title())
            sb.assert_true("Home - RR Absence" in sb.get_page_title())   # PASS expected
            #sb.assert_true("Home - RR Absence #" in sb.get_page_title()) # FAIL expected
            

            # -=-= Sign Up =-=- 

            # sb.click_xpath("/html/body/container/div/container/div/a")

            # # -=-= Login page =-=- 
            # sb.assert_true("Login" in sb.get_page_title(), msg="[TESTING CODE ERROR]: Not on Login-Page")

            # sb.send_keys("/html/body/container/div/div/form/div[1]/div/input", text=USERNAME)
            # sb.send_keys("/html/body/container/div/div/form/div[2]/div/input", text=PASSWORD)
            # # Click "Login"
            # sb.click_xpath("/html/body/container/div/div/form/button")


            # if "Policy" in sb.get_page_title():
            #     # -=-= Policy Page =-=-
            #     sb.click_xpath("/html/body/container/div/div/form/input[2]")
            #     sb.click_xpath("/html/body/container/div/div/form/button")

            # # -=-= Main Calendar Page =-=-
            # sb.click_xpath("/html/body/nav/div[2]/div[1]/a[3]")

            # -=-= Teams Page =-=-
            sb.wait(8)

    

#with SB() as sb:
#    print("[Application]: Running SeleniumBase Commands Now")
#    sb.open(URL)
#    sb.assert_title("Home - RR Absence")
#    sb.click_xpath("/html/body/container/div/container/div/a")
#
#    # -=-= Login page =-=- 
#    sb.assert_true("Login" in sb.get_page_title(), msg="[TESTING CODE ERROR]: Not on Login-Page")
#    
#    sb.send_keys("/html/body/container/div/div/form/div[1]/div/input", text=USERNAME)
#    sb.send_keys("/html/body/container/div/div/form/div[2]/div/input", text=PASSWORD)
#    # Click "Login"
#    sb.click_xpath("/html/body/container/div/div/form/button")
#
#
#    if "Policy" in sb.get_page_title():
#        # -=-= Policy Page =-=-
#        sb.click_xpath("/html/body/container/div/div/form/input[2]")
#        sb.click_xpath("/html/body/container/div/div/form/button")
#    
#    # -=-= Main Calendar Page =-=-
#    sb.click_xpath("/html/body/nav/div[2]/div[1]/a[3]")
#
#    # -=-= Teams Page =-=-
    
#change

    #sb.wait(8)


#class BasicTest(BaseCase):
#    def test_basic(sb):
#        sb.open(URL)
#        sb.assert_title("Home - RR Absence")
        