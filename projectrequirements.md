install Docker 
    - docker --version
    - docker-compose --version

-configure Docker in Django
    1. choose base image
    2. install dependencies

- Docker Compose 
    1. how our Docker images should be used
    2. Define our services
        1. Name 
        2. Port Mapping 
        3. Volume mapping 
    
    - run all commands through Docker compose 
        docker-compose run --rm app sh -c "python manage.py collectstatic"


- Building Images
    - docker build  (building a docker image)
    - 

- creating django project 
     docker-compose run --rm app sh -c "django-admin startproject app ."  (create a app project inside of main project app with name app)


- run developement server
    1. docker-compose up -d (run in detached mode running  our service)

- Writing a test 
    - SimpleTestCase - (No Database)
    - TestCase - (Database)

- Database using 
    postgreSQL
- To Connect Database postgreSQL
   - Psycopg2

    
- Django ORM 
    - Object Relational Mapping (ORM)
    - use any database with django (MySQL, postgreSQL)
    - Django ORM is a high-level interface for interacting with the database. It abstracts away the underlying database and provides a Pythonic way to interact with the data.
    - ORM is a layer of abstraction between the Python code and the database. It allows you to write Python code that interacts with the database without having to write raw SQL.

   |--------------------------------------------------------------------------------------|
     Define Models ---> Generate Migration files ----> Setup Database  ---> Store Data



- Create migrations
    - python manage.py makemigrations



- Creating a our custom user (we are not using Django Default user Model)

