# socialnetworkBackend (acadebeat)

A backend for a **subscription-based social network**, built with Django and Django REST Framework, with social-OAuth login and AWS integration.

## Overview

"acadebeat" is a social platform backend: a custom email-based user model, posts, comments, tagging, follower/subscription relationships, and search. Authentication supports social OAuth providers (Google, Facebook, Twitter, Instagram) alongside email.

## Features

- Custom `User` model (email login) with `PermissionsMixin`
- Posts, comments, and tags (`django-taggit`)
- Follow / subscription relationships between users
- Search across posts/users
- Social OAuth (django-allauth + django-oauth-toolkit + social-oauth2)
- CORS support for a separate front end
- AWS integration (`boto3`/`boto`) and Docker deployment

## Tech Stack

Python · Django 5 · Django REST Framework · PostgreSQL · django-allauth · django-oauth-toolkit · boto3 (AWS) · bcrypt · Docker / docker-compose

## Running

```bash
docker-compose up --build
# or
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Configure database, AWS, and OAuth provider credentials via environment variables. See `test.rest` for example API requests.
