#!/bin/bash

echo "============================================================"
echo "Setting Up Django Project Environment"
echo "This script will make a new venv and install the requirements, then start the Django Project"
echo "This project is tested on Python 3.8. It may not work on other versions"
echo "If this script does not work, you will need to start django manually. This script is only a helper to make it easier to start the project."
echo "Please follow the instructions in the README.txt file to start the project if you need to."
echo "============================================================"


# alias UV temporarily so we can get the path to it without restarting the terminal session
uv_temporary_path="$HOME/.local/bin/uv"
echo "$uv_temporary_path"

# Install UV for faster package management
if ! type "$uv_temporary_path" > /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "uv command found"
    $uv_temporary_path --version
fi

if [ ! -f ".venv/bin/activate" ]; then
    echo "Creating venv ... This may take a while"
    $(uv_temporary_path) venv .venv
fi

if [ ! -f ".env" ]; then
    cp "example_env.txt" ".env"
fi

echo "Installing requirements"
$(uv_temporary_path) pip install -r pyproject.toml --all-extras

if [ -f "ap_src/manage.py" ]; then
    echo "Making migrations"
    ./.venv/bin/python ap_src/manage.py makemigrations

    echo "Running migrations"
    ./.venv/bin/python ap_src/manage.py migrate ap_app
    ./.venv/bin/python ap_src/manage.py migrate

    echo "Creating cache table"
    ./.venv/bin/python ap_src/manage.py createcachetable

    echo "Loading fixtures"
    for f in ap_src/ap_app/fixtures/*.*; do
        echo "Loading fixture $f"
        ./.venv/bin/python ap_src/manage.py loaddata "$f"
    done

    if [ ! -f ".venv/user_created" ]; then
        echo "----------------------------------------------------------------------------------------------------"
        echo "----------------------------------------------------------------------------------------------------"
        echo "Please create an admin user and password. You will need to use this to sign in to the admin panel."
        echo "Please do not use a real password; this is a development environment."
        echo "Create an admin user"

        touch .venv/user_created
        python ap_src/manage.py createsuperuser
    else
        echo "Super User already created"
    fi

    # Uncomment to collect static files
    # echo "Collecting static files"
    # python ap_src/manage.py collectstatic --noinput

    echo "Done"
    echo "Run the web server with:"
    echo "uv run .\ap_src\manage.py runserver"
    echo "Please note that if this is your first time installing uv you may have to restart vscode"
    echo "Alternatively, activate the virtual environment:"
    echo ".\.venv\Scripts\activate"
    echo "And then run the web server with:"
    echo "python ap_src\manage.py runserver"
fi
