# jauth API server

## Pre-requisites
- python >= 3.7

## Callback to external
jauth supports callback request to external url with token for notify some events occurred by jauth to another service.

The base event structure is:
- BaseMessage
```
{
  "issuer": (str)"jauth",
  "issued_at": (int)unix timestamp,
  "token": (str)token for verify that really jauth requested,
  "type": (str)message type
}
```

- User Creation (includes BaseMessage structure)
```
{
  ...BaseMessage,
  "user__id": (str) created user's id,
  "user__email": (str) created user's email,
  "user__third_party_user_id": (str) created user's third party id (if thirdparty user),
  "user__type": (str) created user's type,
  "user__status": (str) created user's status,
  "user__is_email_verified": (bool) created user's email verify status,
  "user__extra": (dict) created user's extra data
}
```

- User Update (includes BaseMessage structure)
```
{
  ...BaseMessage,
  "user__id": (str) created user's id,
  "user__email": (str) created user's email (if email user),
  "user__status": (str) created user's status,
  "user__is_email_verified": (bool) created user's email verify status,
  "user__extra": (dict) created user's extra data
}
```

## Endpoint
### User management

#### Enums
```python
# util/model/user.py
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

  - /-/self:verify *POST*
    - purpose: Verify user with email (Set is_email_verified as True)
    - query_string: `Empty`
    - request:
        ```
        {
            "temp_token": ...temp generated JWT token for verify user
        }
        ```
    - request-header: `Empty`
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

  - /email/self/password:reset *POST*
    - purpose: Reset email user password
    - query_string: `Empty`
    - request:
        ```
        {
            "temp_token": ...temp generated JWT token for reset password ...[str],
            "new_password" ...new password that user wants ...[str]
        }
        ```
    - request-header: `Empty`
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

  - /self *GET*
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


### Internal method

- /internal
  - /token/email_verify *POST*
    - purpose: Create temp token for `/user/-/self/:verify`
    - request:
        ```
        {
          "user_id": ...[str],
        }
        ```
    - request-header:
        ```
        {
          "X-Server-Key": ... internal access key (setup by config when jauth start up) ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": ...token for verify email ...[str],
          "reason": ...,
        }
        ```

  - /users:search *POST*
    - purpose: Find users who fit filters
    - misc:
        ```
        available_order_bys = {
            'id', '-id',
            'email', '-email',
            'created_at', '-created_at',
            'modified_at', '-modified_at'
        }
        ```
    - request:
        ```
        {
            "start": ...Fetch start index...[int],
            "size": ...Fetch size...[int],
            "emails": [
                ...email...[str]
            ],
            "created_at_range": {
                "start": ...iso 8601 format...[str],
                "end": ...iso 8601 format...[str],
            },
            "modified_at_range": {
                "start": ...iso 8601 format...[str],
                "end": ...iso 8601 format...[str],
            },
            "order_bys": [
                ...order by field name...[str]
            ],
            "status": [
                ...UserStatus number...[int]
            ],
            "types": [
                ...UserType number...[int]
            ]
        }
        ```
    - request-header:
        ```
        {
          "X-Server-Key": ... internal access key (setup by config when jauth start up) ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": {
            "total": ...[int],
            "users": [
                {
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
                }
            ]
          },
          "reason": ...,
        }
        ```

  - /token/password_reset *POST*
    - purpose: Create temp token for `/user/email/self/password:reset`
    - request:
        ```
        {
          "user_id": ...[str],
        }
        ```
    - request-header:
        ```
        {
          "X-Server-Key": ... internal access key (setup by config when jauth start up) ...[str]
        }
        ```
    - response:
        ```
        {
          "success": ...,
          "result": ...token for reset email user password ...[str],
          "reason": ...,
        }
        ```