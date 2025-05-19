# Developer Handbook

## Commits

https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/
https://www.conventionalcommits.org/en/v1.0.0-beta.2/

## `.env` Settings File

### Description

The `.env` file is stored in the project root and can either be created manually or is created automatically by the setup script. It looks something like this:

```
TEAM_DATA_URL=http://localhost:8002/
DEBUG=True
PRODUCTION_UI=False
DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
```

If you change the `.env` file, you should reboot the shell/terminal window in which the server is running in order for your changes to take effect.

### Settings Explained

#### `TEAM_DATA_URL`

This is the URL containing the host and port of the server application for the RR Team App. This is needed to pull data about teams and team members from the Team App database using the API. The Team App runs on port 8002 by default. Without a functioning connection to the Team App, the Absence Planner will not function correctly.

#### `DEBUG`

[See the Django documentation for more information about the debug setting](https://docs.djangoproject.com/en/5.1/ref/settings/#debug)

#### `PRODUCTION_UI`

Red UI represents a non-production environment
Blue represents Production.

If you set this to False, it will change the colour of the header in the Absence Planner like this:

![image](https://github.com/user-attachments/assets/49ac875f-ab92-4cc5-bcff-4ae2dd089f67)

If you set this to True, it will change the colour of the header in the Absence Planner like this:

![image](https://github.com/user-attachments/assets/edfd9044-57d0-4e7a-9bc6-8e874df97bee)

#### `DB_*` Options

These set the settings that will be used to connect to the absence planner database.
