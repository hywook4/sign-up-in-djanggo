# Sign-up-in (Django)

---

## Requirements

- python3
- virtualenv (if to run on virtual environment)
- Redis (Need to run redis on localhost:6379)

## Steps to run on local (with virtual env) 
1. Init virtual environment and run virtual environment (required only for virtuam env)
```
virtualenv {VENV_NAME}
ex) virtualenv venv

source {VENV_NAME}/bin/activate
ex) source venv/bin/activate
```
2. Install dependencies (required only for virtuam env)
```
pip install -r requirements.txt
```
3. Run the server
```
python manage.py runserver
```

## APIs

### GET - /sms-auth
Request for SMS authentication


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |


#### Query Parameters
| KEY          | VALUE | REQUIRED |
|--------------| ----- | -------- |
| name         |string      |O        |
| phone_number |string      |O          |


#### Success Response
Code: 200 (success)
Content:
~~~
{{SMS VERFICATION CODE}}
~~~

---

### POST - /sms-auth
Verify the SMS verificationCode


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |


#### Body Parameters
| KEY               | VALUE | REQUIRED |
|-------------------| ----- | -------- |
| name              |string      |O        |
| phone_number      |string       |O          |
| sms_auth_code |string       |O          |


#### Success Response
Code: 200 (success)
Content:
~~~
{
    "name": {NAME_STRING},
    "phoneNumber": {PHONE_NUMBER_STRING},
    "verifiedToken": {SMS_VERIFIED_TOKEN}
}
~~~

---

### POST - /user
Request for sign-up


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |
|X-Sms-VerifiedToken   |{SMS_VERIFIED_TOKEN}       |O        |


#### Body Parameters
| KEY          | VALUE | REQUIRED |
|--------------| ----- | -------- |
| email        |string      |O        |
| nickname     |string       |O          |
| name         |string       |O          |
| phone_number |string       |O          |
| password     |string       |O          |


#### Success Response
Code: 200 (success)
Content:
~~~
{
    "email": {EMAIL_STRING},
    "nickname": {NICK_NAME_STRING},
    "name": {NAME_STRING},
    "phoneNumber": {PHONE_NUMBER_STRING}
}
~~~

---

### PUT - /user
Request change password


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |
|X-Sms-VerifiedToken   |{SMS_VERIFIED_TOKEN}       |O        |


#### Body Parameters
| KEY          | VALUE | REQUIRED |
|--------------| ----- | -------- |
| name         |string      |O        |
| phone_number |string       |O          |
| password     |string       |O          |


#### Success Response
Code: 200 (success)
Content:
~~~

~~~

---

### POST - /user/auth
Request for sign-in


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |


#### Body Parameters
| KEY      | VALUE | REQUIRED |
|----------| ----- | -------- |
| id_field |string("email" or "phone_number"      |O        |
| id_value |string       |O          |
| password |string       |O          |


#### Success Response
Code: 200 (success)
Content:
~~~
{
    "email": {EMAIL_STRING},
    "nickname": {NICK_NAME_STRING},
    "name": {NAME_STRING},
    "phoneNumber": {PHONE_NUMBER_STRING}
    "jwtToken": {JWT_TOKEN}
}
~~~

---

### GET - /user/auth
Request for my info


#### Header
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|Content-Type   |application/json       |O        |
|Authorization   |Bearer {JWT_TOKEN}       |O        |


#### Body Parameters
| KEY  | VALUE | REQUIRED |
| ---- | ----- | -------- |
|      |       |          |


#### Success Response
Code: 200 (success)
Content:
~~~
{
    "email": {EMAIL_STRING},
    "nickname": {NICK_NAME_STRING},
    "name": {NAME_STRING},
    "phoneNumber": {PHONE_NUMBER_STRING}
}
~~~

