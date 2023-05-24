# How to contribute

- Fork this repository
- Clone to your machine
- Create a branch with a name describing the work you are doing
- Add your feature
- Commit and push your work
- Create a pull request
- Star this repository

## **There are two ways to run this app in a development environment**

## With a Python Virtual Environment

- ### Create a Python virtual environment

            python -m venv .venv

- ### Activate virtual environment

            source .venv/bin/activate

- ### Install packages

            pip install -r back_end/requirements.txt

            pip install -r front_end/requirements.txt

- ### To run tests

      pytest

- ### To run WebScraper

      python -m back_end.scraper

- ### To run development server (Flask)

        python -m front_end.wsgi

## Or with Docker

            docker-compose build
            docker-compose up -d
            docker-compose up 
        Open in web browser: http://localhost:8000/

[NGINX Reverse Proxy -> WSGI -> Python/Flask Backend](https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask#nginx-reverse-proxy---wsgi---pythonflask-backend)