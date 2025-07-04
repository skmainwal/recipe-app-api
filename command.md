docker-compose down

docker-compose up


docker-compose build

To Run linting:
docker-compose run --rm app sh -c "flake8"


-To create Django project via docker command:
    docker-compose run --rm app sh -c "django-admin startproject app ."

-To Create a new app:
    docker-compose run --rm app sh -c "django-admin startapp <app_name>"

-To run the docker container (Started project in dev mode):
    docker-compose up


-Github Action Commands:
    1. Coding Linting 2. Unit testing

 Triggering Github Actions:

-NOTE:- Run the test case file 
    docker-compose run --rm app sh -c "python manage.py test"

-DB Connection Cehck
    docker-compose run --rm app sh -c "python manage.py wait_for_db"

Linting issue :
    docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"
    docker-compose run --rm app sh -c "flake8"


Database Migrations:
    Create Migrations:
        docker-compose run --rm app sh -c "python manage.py makemigrations"
    Apply Migrations:
        docker-compose run --rm app sh -c "python manage.py migrate"

    To clear the Database:

        docker volume ls
        docker-compose down

        clear all the data in the database
            docker volume rm <volume_name>



Creating a superuser:
    docker-compose run --rm app sh -c "python manage.py createsuperuser"


Difference between Django and Django Rest Framework:

Django:
    - It is a full-stack web framework that provides a comprehensive set of tools for building web applications.
    - It includes features like database management, authentication, and templating.
    - It is used for building traditional web applications where the server-side logic is executed on the same machine as the web server.

Django Rest Framework:
    - It is a powerful and flexible toolkit for building Web APIs.
    - It is built on top of Django and provides a set of tools for building RESTful APIs.
    - It is used for building APIs that can be consumed by other applications or services.

Difference between APIView vs Viewsets:
    - APIView is a class-based view that provides a set of methods for handling HTTP requests.
    - Viewsets is a class-based view that provides a set of methods for handling HTTP requests.

what is view in django:
    - View is a function or class that handles HTTP requests and returns HTTP responses.

what is viewsets in django:
    - Viewsets is a class-based view that provides a set of methods for handling HTTP requests.

what is the difference between serializers and models:
    - Serializers are used to serialize and deserialize data.
        serializer is used to convert the data into a format that can be sent over the network and vice versa.
        serializer is used to validate the data and to convert the data into a format that can be sent over the network and vice versa.
        deserializer is used to convert the data into a format that can be sent over the network and vice versa.

    - Models are used to define the structure of the data.

