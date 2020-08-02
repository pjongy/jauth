# jauth API server

## Pre-requisites
- python >= 3.7

## Endpoint
### User management

#### Enums
```python
# common/model/user.py
class UserType(enum.IntEnum):
    UNKNOWN = 0
    EMAIL = 1
    GOOGLE = 2
    APPLE = 3
    FACEBOOK = 4
    KAKAO = 5

class UserStatus(enum.IntEnum):
    NORMAL = 0
    DELETED = 1
    WITHDRAWN = 2
```

#### API specs

- /users
  - /-/{user_id} *GET*
    - purpose: Fetch selected user information
    - request: `Empty`
    - response:
        ```
        {
          "success": ...,
          "result": {
            "id": ...uuid of user...[str],
            "email": ...[str],
            "type": ...enum value of UserType...[int],
            "status": ...enum value of UserStatus...[int],
            "extra": ...extra field for free using...[dict],
            "is_email_verified": ...flag for email verified status...[bool],
            "created_at": ...iso 8601 format...[str],
            "modified_at": ...iso 8601 format...[str],
            "account": ...optional existing for email user...[str],
            "third_party_user_id": ...optional existing for non-email user...[str],
          },
          "reason": ...,
        }
        ```

  - /email *POST*
    - purpose: Create email user
    - request:
        ```
        {
          "account": ...,
          "password": ...,
          "email": ...
        }
        ```
    - response: `Same as /users/-/{user_id} GET response`

  - /third_party *POST*
    - purpose: Create third party user
    - request:
        ```
        {
          "user_type": ...enum value of UserType...[int],
          "third_party_token": ...[str]
        }
        ```
    - response: `Same as /users/-/{user_id} GET response`

  - /-/self *GET*
    - purpose: Get passed token's user information
    - request: `Empty`
    - request-header:
        ```
        {
          "Authorization": "Bearer " + ... access token ...[str]
        }
        ```
    - response: `Same as /users/-/{user_id} GET response`

  - /-/self *PUT*
    - purpose: Update user information
    - request:
        ```
        {
          "email": ...[str],
          "extra": ...[dict]
        }
        ```
    - request-header:
        ```
        {
          "Authorization": "Bearer " + ... access token ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": ...[bool],
          "reason": ...,
        }
        ```

  - /email/self/password *PUT*
    - purpose: Update email user's password
    - request:
        ```
        {
          "original_password": ...[str],
          "new_password": ...[str],
        }
        ```
    - request-header:
        ```
        {
          "Authorization": "Bearer " + ... access token ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": ...[bool],
          "reason": ...,
        }
        ```

### Token management

- /token
  - /email *POST*
    - purpose: Get access_token and refresh_token of email user
    - request:
        ```
        {
          "account": ...[str],
          "password": ...[str],
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": {
            "access_token": ...token for authorization...[str],
            "refresh_token": ...token for get new access token...[str]
          },
          "reason": ...,
        }
        ```

  - /third_party *POST*
    - purpose: Get access_token and refresh_token of third party user
    - request:
        ```
        {
          "user_type": ...enum value of UserType...[int],
          "third_party_token": ...[str],
        }
        ```
    - response: `Same as /token/email POST response`

  - /self *POST*
    - purpose: Verify access_token and get token's information (claim)
    - request: `Empty`
    - request-header:
        ```
        {
          "Authorization": "Bearer " + ... access token ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": {
            "iss": ...[str],
            "exp": ...[int],
            "type": ...enum value of UserType...[int],
            "id": ...uuid of user...[str],
          },
          "reason": ...,
        }
        ```

  - / *PUT*
    - purpose: Generate new access_token from refresh_token
    - request:
        ```
        {
          "refresh_token": ...[str],
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": {
            "access_token": ...[str]
          },
          "reason": ...,
        }
        ```