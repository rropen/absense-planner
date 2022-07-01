ECHO OFF
ECHO ============================================================
ECHO Setting Up Django Project Enviroment
ECHO This script will make a new venv and install the requirements, then start the Django Project
ECHO please make sure python is installed and the command to execute it is 'py -3.8'
ECHO This project is tested on Python 3.8. It may not work on other versions
ECHO If this script does not work, you will need to start django manually. This script is only a helper to make it easier to start the project.
ECHO Please follow the instructions in the README.txt file to start the project if you need to.
ECHO ============================================================

SET PYTHON_EXECUTABLE=notfound
@REM LOOP through the list of python commands  to find the correct one by execute the --version of the command and set it to the variable PYTHON_EXECUTABLE of the one which does not throw an error
FOR %%P IN ("python", "python3.8", "py") DO (
    %%~P --version
    IF NOT ERRORLEVEL 1 (
        SET PYTHON_EXECUTABLE=%%~P
        echo Python command found: %%~P
        GOTO :start_django_project
    )
)

IF PYTHON_EXECUTABLE=notfound (
    echo Python command not found. Please install python 3.8 or higher and make sure the command to execute it is 'py -3.8'
    PAUSE
    EXIT
)

:start_django_project

@REM Check if we have a venv
@REM If we do, activate it
@REM If we don't, create it


IF NOT EXIST venv\Scripts\activate.bat (
    ECHO Creating venv ... This may take a while
    %PYTHON_EXECUTABLE% -m venv venv
)

@REM Install requirements if they are not already installed
@REM If they are, skip this step

IF NOT EXIST venv\req_installed  (
    ECHO Installing requirements
	"venv\Scripts\pip" install -r requirements.txt
    COPY NUL venv\req_installed
) ELSE (
    ECHO Requirements already installed
)

@REM Start Django

if EXIST ap_src/manage.py (
    ECHO Making migrations
	"venv\Scripts\python" ap_src/manage.py makemigrations

    ECHO Running migrations
	"venv\Scripts\python" ap_src/manage.py migrate ap_app
	"venv\Scripts\python" ap_src/manage.py migrate

    ECHO Loading fixtures

    @REM LOOP through all fixtures in the fixtures folder in a for loop and load them one by one
    for %%f in (ap_src\ap_app\fixtures\*.*) do (
        ECHO Loading fixture %%f
        "venv\Scripts\python" ap_src/manage.py loaddata %%f
    )

    IF NOT EXIST venv\user_created (
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO Please create and admin user and password, you will need to use this to signin to the admin panel
        ECHO Please do not use a real password this is a development environment.
        ECHO Create an admin user

        COPY NUL venv\user_created
        "venv\Scripts\python" ap_src/manage.py createsuperuser
    ) ELSE (
        ECHO Super User already created
    )

    ECHO Collecting static files
    "venv\Scripts\python" ap_src/manage.py collectstatic --noinput

    ECHO Done
)

PAUSE
