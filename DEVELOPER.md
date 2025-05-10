# Developer Guide

This document provides simple instructions and information for developers who want to contribute to this project or get it running locally. This project is primarily a python based
project.

# Team App Compatibility

Team App must be running for Absence Planner to work correctly. This is because features of the Absence Planner have a hard dependency on the Team App's API in order to work. 

User accounts must be created on the Team App first before creating an account on the Absence Planner. Both accounts must have the same username. This is to avoid instability issues and known errors if you do not have a user on both apps with the same name.

# Setup

## Basic

To start running the application, you need to run the `setup` script:

## Windows

```powershell
.\setup.bat
```

If you get an error saying that you are not permitted to run scripts, run the following command:

```powershell
Set-ExecutionPolicy -Scope CurrentUser Unrestricted
```

## MacOS and Linux

```shell
./setup.sh
```

If you get "permission denied", you need to run the following command:

```shell
chmod +x setup.sh
```

# Dependencies

## Python

You need [Python 3.11.9](https://www.python.org/downloads/release/python-3119/) as this version is what the requirements for specific versions of packages work best with.

## GNU Make

### Overview

To use the `Makefile`, you also need GNU make, which can be installed as follows on different platforms:

### Windows

```sh
winget install ezwinports.make
```

### Linux (Ubuntu)

```sh
sudo apt-get update

sudo apt-get -y install make
```

### MacOS

You will need [Homebrew](https://brew.sh/).

Then simply run

```sh
brew install make
```

## Database Browser

For browsing the sqlite database when working with the Django [ORM](https://docs.djangoproject.com/en/5.2/topics/db/queries/), it is useful to see the state of the database in a static table format. For this, [DB-Browser](https://sqlitebrowser.org/dl/) is a very helpful tool.

You just need to open the `db.sqlite3` found in the source directory in the repository for that application (either Team App or Absence Planner).

## Integrated Development Environment (IDE)

The recommended IDE is Microsoft's Visual Studio Code, but you should be able to use anything you like. The following extensions are recommended for `vscode`:

- Python - allows for intellisense and a language server to enable smart Python development
- Ruff - picks up standardisation and code quality issues in addition to the regular Python extension
- Django - for integration with Django templates and routes

## Astral UV

This project uses [uv](https://docs.astral.sh/uv/) which is a super modern python project tool set built in rust and which is blazingly fast. This one tool system replaces the
dependency manages (pip, poetry, pipenv, pdm, etc.) as well as handles virtual environments, packaging, updating, and even installation of python runtimes. uv uses the
`pyproject.toml` file to record the dependencies and project information rather than the legacy `requirements.txt` file.

# Environment Setup

Although some of this is done by the setup script, if you want you want to manually configure the environment variables, copy the `example_env.txt` file to a new file called `.env` in the root directory. You'll need to fill in values for the database you choose to use. You can set that up locally by
installed something like Postgres, or run your favorite database in docker. Currently, the necessary environment variables are:

| Key              | Value                                |
| ---------------- | ------------------------------------ |
| TEAM_APP_API_URL | The URL of the team data API.        |
| DEBUG            | Set to True to enable debug mode.    |
| PRODUCTION_UI    | Set to True to enable production UI. |
| DB_NAME          | The name of the database.            |
| DB_USER          | The username for the database.       |
| DB_PASSWORD      | The password for the database.       |
| DB_HOST          | The host of the database.            |