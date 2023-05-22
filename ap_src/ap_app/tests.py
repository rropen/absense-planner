import pytest, names
from django.test import TestCase
from parameterized import parameterized
from seleniumbase import BaseCase

# constants for correct credentials
USER = names.get_first_name()
USER1 = names.get_first_name()
USER2 = names.get_first_name()
TEAM = names.get_full_name()
CORRECT_PASSWORD = "Password!1"
# password ids for forms
USERNAME_ID = "#id_username"
PASSWORD_ID = "#id_password"
# password ids for signup page
PASSWORD_ID1 = "#id_password1"
PASSWORD_ID2 = "#id_password2"


class rr_test_cases(BaseCase):

    def auto_signup(self, username = USER, password = CORRECT_PASSWORD):
        """Used a template for typing values in the signup page when testing,
        if not entered the username and password will default to successful values"""
        self.type(USERNAME_ID, username)
        self.type(PASSWORD_ID1, password)
        self.type(PASSWORD_ID2, password)
        self.click('button:contains("Sign Up")')

    @parameterized.expand(
        [["#signup", "Sign Up - RR Absence"], ["#login", "Login - RR Absence"]]
    )
    def test_nav(self, id, title):
        # opens the website to the home page
        self.open("http://127.0.0.1:8000")

        # clicks Signup button
        self.click(id)

        # checks if the page is loaded
        self.assert_title(title)

    @parameterized.expand([["accounts/login"], ["signup"]])
    def test_presence_check(self, page):
        # opens the website to the signup page
        self.open(f"http://127.0.0.1:8000/{page}")
        if "login" in page:
            self.type(USERNAME_ID, "")
            self.type(PASSWORD_ID, "")
        else:
            self.auto_signup(username="", password="")

        # A django error appears which cannot be checked so
        # checking the credentials have not been allowed with the lack of a redirect
        self.assert_url(f"http://127.0.0.1:8000/{page}/")

    @parameterized.expand(
        [
            ["a", "password is too short"],
            ["password", "password is too common"],
            ["12345678", "password is entirely numeric"],
            [USER1, " password is too similar to the username"],
        ]
    )
    def test_signup_password(self, password, err_msg):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")

        # testing password validation
        self.auto_signup(username=USER1, password=password)
        # checking the credentials have not been allowed by making sure it has not left the page
        self.assert_text(err_msg)
    @pytest.mark.order(1)
    def test_signup_correct(self):
        # opens the website to the signup page
        self.open("http://127.0.0.1:8000/signup/")

        # enters correct credentials
        self.auto_signup()

        self.test_login_correct()
        self.click("#terms")
        self.click("#submit")
        
    def test_login_incorrect(self):
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enters incorrect login information
        self.type(USERNAME_ID, "user")
        self.type(PASSWORD_ID, "password")

        # submits form
        self.click('button:contains("Login")')
        # alternate way
        # self.submit("#id_password")

        # check for error message
        self.assert_text("Please enter a correct username and password", ".message")

    def test_login_correct(self):
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enter correct details
        self.type(USERNAME_ID, USER)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)

        # submits form
        self.click('button:contains("Login")')
        self.assert_url("http://127.0.0.1:8000/")

    def test_add_absence(self):
        self.open("http://127.0.0.1:8000/absence/add")
        self.type(USERNAME_ID, USER)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)
        self.click('button:contains("Login")')
        self.assert_url("http://127.0.0.1:8000/absence/add")

        # correct format
        self.type("#id_start_date", "01/01/2023")
        self.type("#id_end_date", "02/01/2023")
        self.click("#submit")
        self.assert_text("Absence successfully recorded")

        # incorrect format
        self.type("#id_start_date", "20/20/2022")
        self.type("#id_end_date", "20/20/2022")
        self.click("#submit")
        self.assert_text("Absence successfully recorded")

    @pytest.mark.order(2)
    @pytest.mark.xfail
    def test_add_recurring(self):
        self.test_login_correct()
        self.click("#absence")
        self.click("#recurring")
        self.click("span:conatins('Add rule')")
        pass

    def test_remove_member(self):
        self.open("http://127.0.0.1:8000/")
        # Registering the "owner"
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[1]')
        self.type('//*[@id="id_username"]', USER1)
        self.type('//*[@id="id_password1"]', "abcABC123@")
        self.type('//*[@id="id_password2"]', "abcABC123@")
        self.click('//*[@id="content"]/div/form/button')
        self.type('//*[@id="id_username"]', USER1)
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        # Creating the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click('//*[@id="content"]/div/div[1]/div[1]/a')
        self.type('//*[@id="nameInput"]', TEAM)
        self.type('//*[@id="id_description"]', 'A team to test removing members from a team.')
        self.click('//*[@id="content"]/div/form/input[2]')
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[2]')

        # Registering a second member
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[1]')
        self.type('//*[@id="id_username"]', USER2)
        self.type('//*[@id="id_password1"]', "abcABC123@")
        self.type('//*[@id="id_password2"]', "abcABC123@")
        self.click('//*[@id="content"]/div/form/button')
        self.type('//*[@id="id_username"]', USER2)
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        # Joining the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click('//*[@id="content"]/div/div[1]/div[2]/a')
        self.click(f'//*[@id={TEAM}]')
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[2]')

        # Logging in as the owner
        self.click('//*[@id="content"]/container/div/a')
        self.type('//*[@id="id_username"]', USER1)
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        # Removing a member from the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click(f'//*[@id="{TEAM}"]')
        self.click('//*[@id="content"]/div/section/div/div[1]/div[2]/a[3]')

        self.click(f'//*[@id="{USER2}"]')
        self.assert_text_not_visible(USER2)
