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

# Tests

## Test 1 - No switch permissions given nor any teams joined

### Expected Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

### Actual Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: set()
- UserProfile usernames who give permissions: set()
- users_sharing_teams: {}
- Redundant switch permissions: None

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: set()
- UserProfile usernames who give permissions: set()
- users_sharing_teams: {}
- Redundant switch permissions: None

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: set()
- UserProfile usernames who give permissions: set()
- users_sharing_teams: {}
- Redundant switch permissions: None

## Test 2 - Switch permissions given from Bob to Billy without sharing any teams

### Expected Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: Billy
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: 2 to 6

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: None
- UserProfile usernames who give permissions: Bob
- users_sharing_teams: None
- Redundant switch permissions: 2 to 6

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

### Actual Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: Billy
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: 2 to 6

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: None
- UserProfile usernames who give permissions: Bob
- users_sharing_team: None
- Redundant switch permissions: 2 to 6

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

## Test 3 - Switch permissions given from Bob to Billy but Billy and Bob are in the same team

### Expected Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: Billy
- UserProfile usernames who give permissions: None
- users_sharing_teams: Billy
- Redundant switch permissions: None

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: None
- UserProfile usernames who give permissions: Bob
- users_sharing_teams: Bob
- Redundant switch permissions: None

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None

### Actual Behaviour

#### Bob

- user_id: 5
- userprofile_id: 2
- User usernames given permissions: Billy
- UserProfile usernames who give permissions: None
- users_sharing_teams: Billy
- Redundant switch permissions: None

#### Billy

- user_id: 6
- userprofile_id: 3
- User usernames given permissions: None
- UserProfile usernames who give permissions: Bob
- users_sharing_team: Bob
- Redundant switch permissions: None

#### Brian:

- user_id: 7
- userprofile_id: 4
- User usernames given permissions: None
- UserProfile usernames who give permissions: None
- users_sharing_teams: None
- Redundant switch permissions: None