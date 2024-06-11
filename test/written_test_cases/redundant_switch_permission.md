# Summary

This is a test case designed to demonstrate how switch permissions are formatted.

It will involve individual accounts for Bob, Billy, and Brian. There will be two teams: Team 1 and Team 2.

Tests will be run in two different stages:

- Stage 1 (Bob and Billy have a team in common (Team 1) and Bob gives Billy switch permissions).
- Stage 2 (Billy then leaves that team (Team 1) and joins Team 2 with Brian)

#  Account Details

## Bob

- Username: "Bob"
- Password: "BobPassword321"
- Email: "bob@gmail.com"

## Billy

- Username: "Billy"
- Password: "BillyPassword321"
- Email: "billy@gmail.com"

## Brian

- Username: "Brian"
- Password: "BrianPassword321"
- Email: "brian@gmail.com"

# Team Details

## Team 1

- Creator: "Bob"
- Members:
    - "Bob"
    - "Billy"

## Team 2

- Creator: "Brian"
- Members:
    - "Brian"

# Test 1 (without fix implemented)

## Description

Test the behaviour of what the 

## Expected Behaviour

### In Bob's Account

#### Stage 1

- "Users with permissions: Bob, Billy"
- "Users sharing teams: Bob, Billy"
- No mention of redundant permissions

#### Stage 2 (Billy Leaves and Joins Brian's Team (Team 2))

- "Users with permissions: Bob, Billy"
- "Users sharing teams: Bob"
- "Redundant permissions found for Billy!"

## Actual Behaviour

#### Stage 1

#### Stage 2 (Billy Leaves and Joins Brian's Team (Team 2))