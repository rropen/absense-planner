from django.test import TestCase
from seleniumbase import BaseCase

class TestCases(BaseCase):
    username = "testuser"
    password = "Password!1"
    USERNAME_ID = "#id_username"
    PASSWORD_ID = "#id_password"
    
    def test_signup(self):
        PASSWORD_ID1 = "#id_password1"
        PASSWORD_ID2 = "#id_password2"
        # opens the website to the home page
        self.open("http://127.0.0.1:8000")
        
        # clicks Signup button
        self.click("#signup")
        
        # checks if the page is loaded
        self.assert_title("Sign Up - RR Absence")
        
        # enters incorrect login information
        # presence check
        self.type(self.USERNAME_ID, "")
        self.type(PASSWORD_ID1, "")
        self.type(PASSWORD_ID2, "")
        self.click('button:contains("Sign Up")')
        self.assert_url("http://127.0.0.1:8000/signup")
        
    def test_login(self):

        # opens the website to the home page
        self.open("http://127.0.0.1:8000")
        
        # clicks login button
        self.click("#login")
        
        # checks if the page is loaded
        self.assert_title("Login - RR Absence")
        
        # enters incorrect login information
        self.type(self.USERNAME_ID, "user")
        self.type(self.PASSWORD_ID, "password")
        
        # submits form
        self.click('button:contains("Login")')
        # alternate way
        #self.submit("#id_password")
        
        # check for error message 
        self.assert_text("Please enter a correct username and password", ".message")
        
        # scroll down
        self.scroll_to_bottom()
        
        # enter correct details
        self.type(self.USERNAME_ID, self.username)
        self.type(self.PASSWORD_ID, self.password)
        
        # submits form
        self.click('button:contains("Login")')
        
    