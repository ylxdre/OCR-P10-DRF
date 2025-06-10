# OCR / DA Python - Project10

## SoftDesk

Build a REST API using DjangoRestFramework

- users, authors, contributors
- projects/issues/comments

-> data models, user model, relations
-> authentication

### Introduction

These instructions allow you to :
- get the program
- install the required environment
- run and use it

### Requirements

1. modules
```
packages : python 3.11, python3.11-venv, python3-pip, git
```

### Installation

1. Clone this repo and go in the project's directory

2. Create the virtual environment
```
python3.11 -m venv env
source env/bin/activate
```

3. install environment 
```
pip install -r requirements.txt
```

## Execution

1. Go in the Django project directory
```
cd softdesk
```
2. Initialize the database
```
python manage.py migrate
```
3. Launch the test's server
```
python manage.py runserver
```
___
## Usage

**URL:**  http://127.0.0.1:8000  

**Authentication :**

Without authentication (no token):
- you can create a user
- you can get the project's list

For any other action a token is required  
To get details of a project you must be contributor  

To create/get detail of issue or to create/get detail of comment you must be contributor to the project

User's management:  
-----

### *User create:* 

-> `POST /api/user/create/`  
<- `201_CREATED` ; `400_BAD_REQUEST`
```
params:

{  
  "username": str,
  "email": str,
  "password": str,
  "password2": str,
  "age": int,
  "can_be_contacted": boolean,
  "can_data_be_shared": boolean
}
```

### *User info:*
*token required*  
-> `GET   /api/user/`   
<- `200_OK / data` 

### *User update:*  
*token required*  
-> `PATCH   /api/user/`  
<- `201_CREATED`; `400_BAD_REQUEST`
```
params:

{  
  "email": str,
  "can_be_contacted": boolean,
  "can_data_be_shared": boolean
}
```

### *Password update:*  

-> `GET /api/user/password-update/`  
<- `204_NO_CONTENT`; `400_BAD_REQUEST`
```
params:

{  
  "old_password": str,
  "new_password": str,
}
```
### *Delete a user*  

*token required*  
-> `DELETE  /api/user/`  
<- `204_NO_CONTENT`; `401_UNAUTHORIZED`  
```
params:

{  
  "user": str
}
```

### *Get token*  

-> `POST  /api/token/`  
<- `200_OK`
```
params
{  
  "username": str,
  "password": str,
}

response
{
  "refresh": "xxxxx",
  "access": "xxxx"
}
```
### *Refresh token*  

-> `POST  /api/token/refresh/`  
<- `200_OK`
```
params
{  
  "username": str,
  "password": str,
  "refresh": "xxxxxx"
}

response
{
  "refresh": "xxxxx",
  "access": "xxxx"
}
```

Project:
---
### *Retrieve the list of projects*
-> `GET /api/project/`  
<- `200_OK / data`; `403_FORBIDDEN`
```
querystrings

?contributor={user}
?author={user}
```

### *Create a project*
-> `POST /api/project/`  
<- `200_OK / data`; `403_FORBIDDEN`
```
params:

{  
  "title": str,
  "type": 
    "choices": [
          {
            "value": "BackEnd",
          },
          {
            "value": "FrontEnd",
          },
          {
            "value": "iOS",
          },
          {
            "value": "Android",
          },
  "description": str,
}
```
### *Get project's detail*
*token required*  
-> `GET /api/project/{id}/`  
<- `200_OK / data`; `403_FORBIDDEN`

### *Update a project*
*token required*  
-> `PATCH /api/project/{id}/`  
<- `200_OK / data`; `403_FORBIDDEN`
```
params:

{  
  "title": str,
  "type": 
    "choices": [
          {
            "value": "BackEnd",
          },
          {
            "value": "FrontEnd",
          },
          {
            "value": "iOS",
          },
          {
            "value": "Android",
          },
  "description": str,
}
```
### *Add a contributor to a project*
*token required*  

-> `PATCH /api/project/{id}/contributor/`  
<- `202_ACCEPTED`; `403_FORBIDDEN`
```
params:

{
  "contributor": {username}
}
```
### *Delete a project*
*token required*  
-> `DELETE /api/project/{id}/`  
<- `204_NO_CONTENT`; `403_FORBIDDEN`

Issue:
---
### *List issues (where requestor is contributor)*
*token required*  
-> `GET /api/issue/`  
<- `200_OK`

### *Create an issue*
*token required*  
-> `POST /api/issue/`  
<- `201_CREATED / data`; `403_FORBIDDEN`
```
params:

{
  "title": str,
  "project": int,
  "description": str,
  "priority":
       "choices": [
          {
            "value": "Low",
          },
          {
            "value": "Medium",
          },
          {
            "value": "High",
          }
      ]
  "tag":        
        "choices": [
          {
            "value": "Bug",
          },
          {
            "value": "Feature",
          },
          {
            "value": "Task",
          }
        ]
  "status":  
        "choices": [
          {
            "value": "ToDo",
          },
          {
            "value": "In Progress",
          },
          {
            "value": "Finished",,
          }
        ]
}
```
### *Update an issue*
*token required*  
-> `PATCH /api/issue/{id}/`  
<- `200_OK / data`; `403_FORBIDDEN`

/!\ Only the author of an issue can affect it  
(update to another author)

### *Delete an issue*
*token required*  
-> `DELETE /api/issue/{id}/`  
<- `204_NO_CONTENT`; `403_FORBIDDEN`

### *Retrieve contributors for a given issue*
*token required*  
-> `GET /api/issue/{id}/contributors/`  
<- `200_OK`; `403_FORBIDDEN`

Comment:
---
### *Create a comment*
*token required*  
-> `POST /api/comment/`  
<- `201_CREATED / data`; `403_FORBIDDEN`
```
params:

{
  "title": str,
  "issue": int,
  "description": str
}
```

### *Update a comment*
*token required*  
-> `PATCH /api/comment/{id}/`  
<- `200_OK / data`; `403_FORBIDDEN`

### *Delete a comment*
*token required*  
-> `DELETE /api/comment/{id}/`  
<- `204_NO_CONTENT`; `403_FORBIDDEN`
___
## Author

YaL  <yann@needsome.coffee>

## License

MIT License  
Copyright (c) 2025 

