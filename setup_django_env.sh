#!/bin/bash

echo "============================================================"
echo "Setting Up Django Project Environment"
echo "This script will make a new venv and install the requirements, then start the Django Project"
echo "This project is tested on Python 3.8. It may not work on other versions"
echo "If this script does not work, you will need to start django manually. This script is only a helper to make it easier to start the project."
echo "Please follow the instructions in the README.txt file to start the project if you need to."
echo "============================================================"

PYTHON_EXECUTABLE="notfound"

for CMD in python3 python; do
    if command -v "$CMD" &> /dev/null; then
        $CMD --version
        PYTHON_EXECUTABLE=$CMD
        echo "Python command found: $CMD"
        break
    fi
done

if [ "$PYTHON_EXECUTABLE" = "notfound" ]; then
    echo "Python command not found. Please install Python 3.8 or higher and make sure it is in your PATH."
    exit 1
fi

if [ ! -f "venv/bin/activate" ]; then
    echo "Creating venv ... This may take a while"
    $PYTHON_EXECUTABLE -m venv venv
fi

if [ ! -f ".env" ]; then
    cp "example_env.txt" ".env"
fi

if [ ! -f "venv/req_installed" ]; then
    echo "Installing requirements"
    source venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    touch venv/req_installed
    deactivate
else
    echo "Requirements already installed"
fi

if [ -f "ap_src/manage.py" ]; then
    source venv/bin/activate

    echo "Making migrations"
    python ap_src/manage.py makemigrations

    echo "Running migrations"
    python ap_src/manage.py migrate ap_app
    python ap_src/manage.py migrate

    echo "Loading fixtures"
    for f in ap_src/ap_app/fixtures/*.*; do
        echo "Loading fixture $f"
        python ap_src/manage.py loaddata "$f"
    done

    if [ ! -f "venv/user_created" ]; then
        echo "----------------------------------------------------------------------------------------------------"
        echo "----------------------------------------------------------------------------------------------------"
        echo "Please create an admin user and password. You will need to use this to sign in to the admin panel."
        echo "Please do not use a real password; this is a development environment."
        echo "Create an admin user"

        touch venv/user_created
        python ap_src/manage.py createsuperuser
    else
        echo "Super User already created"
    fi

    # Uncomment to collect static files
    # echo "Collecting static files"
    # python ap_src/manage.py collectstatic --noinput

    echo "Done"
    echo "Don't forget to activate the virtual environment before running manage.py"
    deactivate
fi
