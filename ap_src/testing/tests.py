# Pip install seleniumbase on college laptops by doing - "python -m pip install selenium-base"
import names
import pytest
from django.test import TestCase
from parameterized import parameterized
from seleniumbase import BaseCase

# constants for username credentials
USER = names.get_first_name()
USER1 = names.get_first_name()
USER2 = names.get_first_name()
TEAM = names.get_full_name().replace(" ", "")
CORRECT_PASSWORD = "Password!1"
# username and password ids for login
USERNAME_ID = "#id_username"
PASSWORD_ID = "#id_password"
# password ids for signup page
PASSWORD_ID1 = "#id_password1"
PASSWORD_ID2 = "#id_password2"

URL = "http://LocalHost:8000/"

# Hard-Coded temp values
USERNAME = "patrick"
PASSWORD = "password"


class BasicTest(BaseCase):
    def test_basic(self):
        self.open(URL)
        self.assert_title("Home - RR Absence")
        self.click("#login")

        # -=-= Login page =-=-
        self.assert_true(
            "Login" in self.get_page_title(),
            msg="[TESTING CODE ERROR]: Not on Login-Page",
        )

        self.send_keys(USERNAME_ID, text=USERNAME)
        self.send_keys(PASSWORD_ID, text=PASSWORD)
        # Click "Login"
        self.click("#submit")

        if "Policy" in self.get_page_title():
            # -=-= Policy Page =-=-
            self.click("#terms")
            self.click("#submit")

        # -=-= Main Calendar Page =-=-

        self.click("#home")

        # -=-= Teams Page =-=-

        self.wait(3)


class RRTestCases(BaseCase):
    def auto_signup(self, username=USER, password=CORRECT_PASSWORD):
        """Used a template for typing values in the signup page when testing,
        if not entered the username and password will default to successful values"""
        self.type(USERNAME_ID, username)
        self.type(PASSWORD_ID1, password)
        self.type(PASSWORD_ID2, password)
        self.click('button:contains("Sign Up")')

    @parameterized.expand(
        [["#signup", "Sign Up - RR Absence"], ["#login", "Login - RR Absence"]]
    )
    def test_nav(self, nav_id, title):
        # opens the website to the home page
        self.open("http://127.0.0.1:8000")

        # clicks Signup button
        self.click(nav_id)

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
    @pytest.mark.skip()
    def test_add_recurring(self):
        self.test_login_correct()
        self.click("#absence")
        self.click("#recurring")
        self.click("span:conatins('Add rule')")

    @pytest.mark.order(3)
    def test_teams_join(self):
        self.open("http://127.0.0.1:8000/signup")
        self.auto_signup(username=USER1)
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enter correct details
        self.type(USERNAME_ID, USER1)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)

        # submits form
        self.click('button:contains("Login")')
        self.click("#terms")
        self.click("#submit")
        # User 2
        self.open("http://127.0.0.1:8000/signup")
        self.auto_signup(username=USER2)
        # opens the website to the login page
        self.open("http://127.0.0.1:8000/accounts/login")

        # enter correct details
        self.type(USERNAME_ID, USER2)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)

        # submits form
        self.click('button:contains("Login")')
        self.click("#terms")
        self.click("#submit")
        self.click("#teams")

    def test_teams_remove_member(self):
        self.open("http://127.0.0.1:8000/accounts/login")
        # Logging in the "owner"

        self.type(USERNAME_ID, USER1)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)
        self.click("#submit")

        # Creating the team
        self.click("#teams")
        self.click("#create")
        self.type("#nameInput", TEAM)
        self.type("#id_description", "A team to test removing members from a team.")
        self.click("#submit")
        self.click("#logout")

        # logs in member
        self.open("http://127.0.0.1:8000/accounts/login")
        # enter correct details
        self.type(USERNAME_ID, USER2)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)
        self.click("#submit")

        # Joining the team
        self.click("#teams")
        self.click("#join")
        self.click(f"#join_member_{TEAM}")
        self.click("#logout")

        # Logging in as the owner
        self.click("#login")
        self.type(USERNAME_ID, USER1)
        self.type(PASSWORD_ID, CORRECT_PASSWORD)
        self.click("#submit")

        # Removing a member from the team
        self.click("#teams")
        self.click(f"#{TEAM}")
        self.click("#settings")

        self.click(f"#remove_{USER2}")
        self.assert_text_not_visible(USER2)
