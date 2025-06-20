# Developer Guide

## Brief Overview

This document provides simple instructions and information for anybody who wishes to create pull requests and pass pre-commit and CI checks and tests.

To contribute changes to the original respository, the following commands can be used:

- `git remote add upstream ORIGINAL_REPOSITORY_URL`

- `git merge upstream/master git fetch upstream`

- `git merge upstream/master`

- `git push origin master`

## Commits

In order to pass automated pre-commit checks, this is important reading material.

- [**IMPORTANT** Conventional commits specification you *must* follow](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- [Complementary material for writing conventional commits](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type)
- [Guide to writing good commit messages](https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/)