from django.test import TestCase
from seleniumbase import BaseCase

# Create your tests here.

class rr_test_cases(BaseCase):

    def test_remove_member(self):
        self.open("http://127.0.0.1:8000/")
        #Registering the "owner"
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[1]')
        self.type('//*[@id="id_username"]', 'testingusername')
        self.type('//*[@id="id_password1"]', "abcABC123@")
        self.type('//*[@id="id_password2"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.type('//*[@id="id_username"]', 'testingusername')
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        #Creating the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click('//*[@id="content"]/div/div[1]/div[1]/a')
        self.type('//*[@id="nameInput"]', 'Test Team')
        self.type('//*[@id="id_description"]', 'A team to test removing members from a team.')
        self.click('//*[@id="content"]/div/form/input[2]')
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[2]')

        #Registering a second member
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[1]')
        self.type('//*[@id="id_username"]', 'testmember')
        self.type('//*[@id="id_password1"]', "abcABC123@")
        self.type('//*[@id="id_password2"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.type('//*[@id="id_username"]', 'testmember')
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        #Joining the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click('//*[@id="content"]/div/div[1]/div[2]/a')
        self.click('//*[@id="Test Team"]')
        self.click('//*[@id="navbarExampleTransparentExample"]/div[2]/div/div/div/a[2]')

        #Logging in as the owner
        self.click('//*[@id="content"]/container/div/a')
        self.type('//*[@id="id_username"]', 'testingusername')
        self.type('//*[@id="id_password"]', 'abcABC123@')
        self.click('//*[@id="content"]/div/form/button')
        self.click('//*[@id="terms"]')
        self.click('//*[@id="content"]/div/form/button')

        #Removing a member from the team
        self.click('//*[@id="navbarExampleTransparentExample"]/div[1]/a[3]')
        self.click('//*[@id="Test Team"]')
        self.click('//*[@id="content"]/div/section/div/div[1]/div[2]/a[3]')
        self.click('//*[@id="testmember"]')
        self.assert_text_not_visible("testmember")