# Developer Guide

## Brief Overview

This document provides simple instructions and information for developers who want to contribute to this project or get it running locally. This project is primarily a python based
project.

## Contributing

To learn more about contributing (e.g., commits, pull requests, etc.), read our [Contributer's Guide](CONTRIBUTING.md)

## Team App Compatibility

Team App must be running for Absence Planner to work correctly. This is because features of the Absence Planner have a hard dependency on the Team App's API in order to work.

User accounts must be created on the Team App first before creating an account on the Absence Planner. Both accounts must have the same username. This is to avoid instability issues and known errors if you do not have a user on both apps with the same name.

## Setup

### Basic

To start running the application, you need to run the `setup` script:

### Windows

```powershell
.\setup.bat
```

If you get an error saying that you are not permitted to run scripts, run the following command:

```powershell
Set-ExecutionPolicy -Scope CurrentUser Unrestricted
```

### MacOS and Linux

```shell
./setup.sh
```

If you get "permission denied", you need to run the following command:

```shell
chmod +x setup.sh
```

## Dependencies

### Python

You need [Python 3.11.9](https://www.python.org/downloads/release/python-3119/) as this version is what the requirements for specific versions of packages work best with.

### GNU Make

#### Overview

To use the `Makefile`, you also need GNU make, which can be installed as follows on different platforms:

#### Windows

```sh
winget install ezwinports.make
```

#### Linux (Ubuntu)

```sh
sudo apt-get update

sudo apt-get -y install make
```

#### MacOS

You will need [Homebrew](https://brew.sh/).

Then simply run

```sh
brew install make
```

### Database Browser

For browsing the sqlite database when working with the Django [ORM](https://docs.djangoproject.com/en/5.2/topics/db/queries/), it is useful to see the state of the database in a static table format. For this, [DB-Browser](https://sqlitebrowser.org/dl/) is a very helpful tool.

You just need to open the `db.sqlite3` found in the source directory in the repository for that application (either Team App or Absence Planner).

### Integrated Development Environment (IDE)

The recommended IDE is Microsoft's Visual Studio Code, but you should be able to use anything you like. The following extensions are recommended for `vscode`:

- Python - allows for intellisense and a language server to enable smart Python development
- Ruff - picks up standardisation and code quality issues in addition to the regular Python extension
- Django - for integration with Django templates and routes

### Astral UV

This project uses [uv](https://docs.astral.sh/uv/) which is a super modern python project tool set built in rust and which is blazingly fast. This one tool system replaces the
dependency manages (pip, poetry, pipenv, pdm, etc.) as well as handles virtual environments, packaging, updating, and even installation of python runtimes. uv uses the
`pyproject.toml` file to record the dependencies and project information rather than the legacy `requirements.txt` file.

### Node

#### Overview

To access various features such as pre-commit and pre-push hooks, you will need Node JS and its package manager, NPM.

#### Windows

To install the Node Version Manager on Windows, do:

```powershell
winget install nvs
```

Reboot your powershell and simply run:

```powershell
nvs
```

...and it should let you install a version of Node. Then reboot your PC, and you should have access to Node JS.

#### Linux (Ubuntu)

Run the following if you use the `apt` package manager:

```bash
sudo apt-get update
sudo apt install curl
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
```

Reboot your terminal and run:

```bash
nvm
```

...and choose the version of Node JS that you want.

#### MacOS

```zsh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | zsh
```

## Environment Setup

### Instructions

Although some of this is done by the setup script, if you want you want to manually configure the environment variables, copy the `example_env.txt` file to a new file called `.env` in the root directory. You'll need to fill in values for the database you choose to use. You can set that up locally by
installed something like Postgres, or run your favorite database in docker. Currently, the necessary environment variables are:

### `.env` Settings File

#### Description

The `.env` file is stored in the project root and can either be created manually or is created automatically by the setup script. It looks something like this:

```
TEAM_APP_API_URL=http://localhost:8002/api/
# API key for development use only (DO NOT USE IN PRODUCTION)
TEAM_APP_API_KEY="Api-Key amAaQwQ0.cmf6FJ6OcfpBrk5frt744653z4pwll1I"
TEAM_APP_API_TIMEOUT=6

DEBUG=True
PROFILING=False
PRODUCTION_UI=False

DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
```

If you change the `.env` file, you should reboot the shell/terminal window in which the server is running in order for your changes to take effect.

#### Settings Explained

##### `TEAM_APP_API_URL`

This is the URL containing the host and port of the server application for the [RR Team App](https://github.com/rropen/team-app)'s REST API. This is needed to pull data about teams and team members from the Team App database using the API. The Team App runs on port 8002 by default. Without a functioning connection to the Team App, the Absence Planner will not function correctly.

##### `TEAM_APP_API_KEY`

This is the API key used to access the Team App API. This exists because the Team App API is a private API, meaning you can only access it if you have a key. Only app that are trusted to access and modify data in the deployed Team App have this key, such as the Absence Planner.

A development API key is provided in the form of a fixture on the Team App and an example env variable here on the Absence Planner. ***DO NOT*** use the provided development API key in production because it is available online. It is used only as sample data to make developers' and contributers' lives easier when developing.

##### `TEAM_APP_API_TIMEOUT`

This is a number that represents the seconds it takes for the Absence Planner to timeout when connecting to the Team App to send requests (server-to-server communication using the API).

##### `DEBUG`

[See the Django documentation for more information about the debug setting.](https://docs.djangoproject.com/en/5.1/ref/settings/#debug)

##### `PROFILING`

On the Absence Planner, this is for enabling the [`django-debug-toolbar`](https://github.com/django-commons/django-debug-toolbar) in order to analyse requests whilst interacting with the application. This was initially added to investigate slow API requests, but is quite versatile and can be used for many more purposes.

##### `PRODUCTION_UI`

Red UI represents a non-production environment
Blue represents Production.

If you set this to False, it will change the colour of the header in the Absence Planner like this:

![image](https://github.com/user-attachments/assets/49ac875f-ab92-4cc5-bcff-4ae2dd089f67)

If you set this to True, it will change the colour of the header in the Absence Planner like this:

![image](https://github.com/user-attachments/assets/edfd9044-57d0-4e7a-9bc6-8e874df97bee)

##### `DB_*` Options

These set the settings that will be used to connect to the absence planner database.

