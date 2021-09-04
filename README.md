What Is This?

This is a Python/Django application intended to provide a working microservice for mobile APIs. The goal of these endpoints is to be simple, well-documented and to provide a base for developers to develop other applications off of.

How To Use This

First create local postgres database and update database credentials in settings.py file.
Run makemigrations command "python manage.py makemigrations"
& then run migrate command "python manage.py migrate"

Run pip install -r requirements.txt to install dependencies
Run python manage.py runserver
Navigate to http://localhost:8000 in your browser


Making Requests
The base url for web api's are http://localhost:8000/web/vi/
The base url for mobile api's are http://localhost:8000/api/vi/
/store/v1/weburls.py file contains endpoint for web api's
/store/v1/apiurls.py file contains endpoint for mobile api's
