# Getting started with SeleniumBase
SeleniumBase is an automated testing module for Python, that we will be using in our project in order to run quick and efficient tests on the application before we finalise our changes. SeleniumBase is an improved version of Selenium using Pytest.

## Installing SeleniumBase
There are two ways to install SeleniumBase: either by cloning the repository with Git or using pip to install it.
With Git:

    git  clone  https://github.com/seleniumbase/SeleniumBase.git
    cd  SeleniumBase/
    pip  install  -e  .

With pip:

    pip  install  seleniumbase

##  Example Syntax
To get started with SeleniumBase in your project, first, you have to import the code into your file

    import seleniumbase

After this, you'll need to define your test case class.

    class test_cases(BaseCase):
The `BaseCase` argument indicates that the tests in this class are SeleniumBase tests.
Next, you have to create a test case. In this instance, we're going to test registering a user, so we'll call it `test_register_account.` **Please note that your test cases have to start with "test_" or else Pytest won't recognise it!**

    class test_cases(BaseCase):
	    
	    def test_register_account(self):
This is the test case defined. In order for SeleniumBase to start to test our project, we need to have it open our website, which by default is on https://127.0.0.1:8000.

    class test_cases(BaseCase):
	    
	    def test_register_account(self):
		    
		    self.open("https://127.0.0.1:8000")
`self.open()`, as the name implies, opens up a website defined by the URL. 
Now, we have to make SeleniumBase input a username in the username field.

    class test_cases(BaseCase):
	    
	    def test_register_account(self):
		    
		    self.open("https://127.0.0.1:8000")
			
			self.type("#id_username", "TestUsername")
`self.type()` takes in an argument for a text box that SeleniumBase should enter text into, as well as the text it should enter into the element. This can either be done through the element's ID (which is preferable) or the element's xpath, which is obtained through inspecting the element, right-clicking and selecting "copy xpath" or "copy full xpath".
Next, we have to repeat the same step with the password and confirm password fields.

    class test_cases(BaseCase):
	    
	    def test_register_account(self):
		    
		    self.open("https://127.0.0.1:8000")
			
			self.type("#id_username", "TestUsername")

			self.type(#id_password1", "abcABC123@")

			self.type("#id_password2", "abcABC123@")

Now that all the fields are filled, we can make SeleniumBase click the register button. This is done through `self.click()`, which simply clicks on a defined element on the page.

    class test_cases(BaseCase):
	    
	    def test_register_account(self):
		    
		    self.open("https://127.0.0.1:8000")
			
			self.type("#id_username", "TestUsername")

			self.type(#id_password1", "abcABC123@")

			self.type("#id_password2", "abcABC123@")

			self.click("#signup")

Now, enter the terminal and use this function to run the Django project.

    python manage.py runserver
And then create a new terminal and run this command:

    pytest ap_app/test.py --demo
This should run through your test, and if everything worked fine, then you've ran your first successful test.
The `--demo` argument means that SeleniumBase will run through each step of the test individually.

    pytest ap_app/tests.py -v 
The `-v` arguement makes the output in the command line more detailed, and includes which tests passed and which failed aswell as where each one went wrong.

    pytest ap_app/tests.py -k absence
The `-k` arguement lets you run only tests which contain the next arguement typed in, for example here it would only run tests with absence in the name. 
