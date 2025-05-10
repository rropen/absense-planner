# Developer Guide

This document provides simple instructions and information for developers who want to contribute to this project or get it running locally. This project is primarily a python based
project.

## Environment Setup

Copy the `.env.example` file to a new file called `.env` in the root directory. You'll need to fill in values for the database you choose to use. You can set that up locally by
installed something like Postgres, or run your favorite database in docker. Currently, the necessary environment variables are:

| Key           | Value                                |
| ------------- | ------------------------------------ |
| TEAM_DATA_URL | The URL of the team data API.        |
| DEBUG         | Set to True to enable debug mode.    |
| PRODUCTION_UI | Set to True to enable production UI. |
| DB_NAME       | The name of the database.            |
| DB_USER       | The username for the database.       |
| DB_PASSWORD   | The password for the database.       |
| DB_HOST       | The host of the database.            |

## Dependencies

This project uses [uv](https://docs.astral.sh/uv/) which is a super modern python project tool set built in rust and which is blazingly fast. This one tool system replaces the
dependency manages (pip, poetry, pipenv, pdm, etc.) as well as handles virtual environments, packaging, updating, and even installation of python runtimes. uv uses the
`pyproject.toml` file to record the dependencies and project information rather than the legacy `requirements.txt` file.
