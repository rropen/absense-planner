import pytest
from django.test import TestCase
from seleniumbase import BaseCase

# constants for correct credentials
CORRECT_USERNAME = "testuser"
CORRECT_PASSWORD = "Password!1"
# password ids for forms
USERNAME_ID = "#id_username"
PASSWORD_ID = "#id_password"
@pytest.mark.order1
class TestSignup(BaseCase):
    """Conatins all tests for the signup page"""
    # password ids for signup page
    PASSWORD_ID1 = "#id_password1"
    PASSWORD_ID2 = "#id_password2"

    def auto_signup(self, username = CORRECT_USERNAME, password = CORRECT_PASSWORD):
        """Used a template for typing values in the signup page when testing,
         if not entered the username and password will default to successful values"""
        self.type(USERNAME_ID, username)
        self.type(self.PASSWORD_ID1, password)
        self.type(self.PASSWORD_ID2, password)
        self.click('button:contains("Sign Up")')

    def test_nav(self):
        # opens the website to the home page
        self.open("http://127.0.0.1:8000")
        
        # clicks Signup button
        self.click("#signup")
        
        # checks if the page is loaded
        self.assert_title("Sign Up - RR Absence")

    def test_presence(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")     
        
        # presence check
        self.auto_signup(username="", password = "")
        
        # A django error appears which cannot be checked so
        # checking the credentials have not been allowed with the lack of a redirect
        self.assert_url("http://127.0.0.1:8000/signup/")

    def test_username(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")  

        # type checks

        self.auto_signup(username="!")
        # checking the error message
        self.assert_text("Enter a valid username") 

        self.auto_signup(username=":")
        # checking for error text
        self.assert_text("Enter a valid username") 

        self.auto_signup(username="%")
        # checking for error text
        self.assert_text("Enter a valid username")

    def test_password(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")  

        # testing password validation 

        self.auto_signup(password="a")
        # checking the credentials have not been allowed by making sure it has not left the page
        self.assert_url("http://127.0.0.1:8000/signup/")

    def test_correct(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")  

        # enters correct credentials
        self.auto_signup()


class TestLogin(BaseCase):
    """Contains all tests for login page"""
    def test_nav(self):

        # opens the website to the home page
        self.open("http://127.0.0.1:8000")
        
        # clicks login button
        self.click("#login")
        
        # checks if the page is loaded
        self.assert_title("Login - RR Absence")

    def test_presence(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/accounts/login/")     
        
        # presence check
        self.type(USERNAME_ID, "")
        self.type(PASSWORD_ID, "")
        
        # A django error appears which cannot be checked so
        # checking the credentials have not been allowed with the lack of a redirect
        self.assert_url("http://127.0.0.1:8000/accounts/login/")
        
    def test_incorrect(self):
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enters incorrect login information
        self.type(USERNAME_ID, "user")
        self.type(PASSWORD_ID, "password")
        
        # submits form
        self.click('button:contains("Login")')
        # alternate way
        #self.submit("#id_password")
        
        # check for error message 
        self.assert_text("Please enter a correct username and password", ".message")
        
    def test_correct(self):
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enter correct details
        self.type(USERNAME_ID, CORRECT_USERNAME)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)
        
        # submits form
        self.click('button:contains("Login")')
        