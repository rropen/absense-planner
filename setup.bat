ECHO OFF
ECHO ============================================================
ECHO Setting Up Django Project Enviroment
ECHO This script will make a new venv and install the requirements, then start the Django Project
ECHO This project is tested on Python 3.8. It may not work on other versions
ECHO If this script does not work, you will need to start django manually. This script is only a helper to make it easier to start the project.
ECHO Please follow the instructions in the README.txt file to start the project if you need to.
ECHO ============================================================

@REM Install UV for faster package management
uv --version
IF NOT ERRORLEVEL 1 (
    ECHO uv command found
) ELSE (
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    @REM alias UV temporarily so we can get the path to it without restarting the terminal session
    doskey uv=$HOME\.local\bin\uv
    doskey uvx=$HOME\.local\bin\uvx
)

:start_django_project

@REM Check if we have a venv
@REM If we do, activate it
@REM If we don't, create it

IF NOT EXIST .venv\Scripts\activate.bat (
    ECHO Creating venv ... This may take a while
    uv venv .venv
)

@REM Create the .env file

COPY "example_env.txt" ".env"

@REM Install requirements

ECHO Installing requirements
uv pip install -r pyproject.toml --all-extras

@REM Start Django

if EXIST ap_src/manage.py (
    ECHO Making migrations
	".venv\Scripts\python" ap_src/manage.py makemigrations

    ECHO Running migrations
	".venv\Scripts\python" ap_src/manage.py migrate ap_app
	".venv\Scripts\python" ap_src/manage.py migrate

    ECHO Creating cache table
    ".venv\Scripts\python" ap_src/manage.py createcachetable

    ECHO Loading fixtures

    @REM LOOP through all fixtures in the fixtures folder in a for loop and load them one by one
    for %%f in (ap_src\ap_app\fixtures\*.*) do (
        ECHO Loading fixture %%f
        ".venv\Scripts\python" ap_src/manage.py loaddata %%f
    )

    IF NOT EXIST ".venv\user_created" (
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO Please create and admin user and password, you will need to use this to signin to the admin panel
        ECHO Please do not use a real password this is a development environment.
        ECHO Create an admin user

        COPY NUL ".venv\user_created"
        ".venv\Scripts\python" ap_src/manage.py createsuperuser
    ) ELSE (
        ECHO Super User already created
    )

    @REM ECHO Collecting static files
    @REM only needed for deployment
    @REM ".venv\Scripts\python" ap_src/manage.py collectstatic --noinput

    ECHO Done
    ECHO Run the web server with:
    ECHO uv run .\ap_src\manage.py runserver
    ECHO Alternatively, activate the virtual environment:
    ECHO .\.venv\Scripts\activate
    ECHO And then run the web server with:
    ECHO python ap_src\manage.py runserver
)

PAUSE
