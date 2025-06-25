<p>
    <img alt="Rolls-Royce Logo" width="100" src="https://raw.githubusercontent.com/rropen/.github/main/img/logo.png">
    <br>
    A web app absence planner for teams
</p>

<!-- Place any useful shield.io shields here.  Use the style=flat styling option. -->
<p>
 <a href=""><img src="https://img.shields.io/badge/Rolls--Royce-Software%20Factory-10069f"></a>
 <a href="http://commitizen.github.io/cz-cli/"><img src="https://img.shields.io/badge/commitizen-friendly-brightgreen?style=flat"></a>
</p>

# Absence Planner

![image](https://github.com/user-attachments/assets/9678cdf2-012e-4f7a-8919-24a4cd0f7279)

---

## Overview

Although R-R has existing systems to manage and view absence, they fail to meet some basic needs.

1. Allow any R-R computer user to view any colleagues absence information (with appropriate protection of people's data and compliance to any legistation on privacy)
2. Include 3rd party colleagues/contractors as well as regular staff
3. globally accessible

This project aims to overcome these deficiencies

## Usage

### Background

This project is just starting, will be a django web app with Javascript/jQuery on the front end, and Bulma.io CSS

### Running the Server

Once you have followed the [instructions in the Developer Guide for setting up the application](DEVELOPER.md#setup), you can simply run the server with `uv`:

```shell
uv run ap_src/manage.py runserver
```

If you are jumping from setup to this and the system cannot find the `uv` command, you may have to restart your IDE or device.

## Developer Guide

To get started with the Absence Planner and the Team App, we have a [developer guide](DEVELOPER.md).

## Contributing

To learn more about contributing (e.g., commits, pull requests, etc.), read our [Contributer's Guide](CONTRIBUTING.md)

## Colour Schemes

- Options for modifying colour schemes can be found in the profile settings page, under the "App Information" category. Different colours can be picked for altering Bank Holidays and Weekends. A dropdown list within the same container can be modified to choose whether these specific dates are shown on the calendar. The rectangular bar can be selected to show a colour picker where a specific colour can be chosen, after these changes have been made they can be confirmed by clicking on the "Submit" button to apply them.
