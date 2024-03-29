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

            pip install -r web_scraper/requirements.txt

            pip install -r api/requirements.txt

- ### To run tests

      python -m pytest

- ### To run WebScraper

  - copy/paste the `sample.env` contents into a new file named `.env`
  - Get a [Google Geocoding API key](https://developers.google.com/maps/documentation/geolocation/overview)
  - Update the environmental variable `GV3_API_KEY` with your API Key
  - Then run:

          python -m web_scraper.scraper

- ### To run development server (Flask)

            python -m api.wsgi

## Or with Docker

### To Run Scraper

            docker-compose -f scraper.yaml build
            docker-compose -f scraper.yaml up

### To run development server (flask)

            docker-compose build
            docker-compose up
        Open in web browser: http://localhost:8000/

[NGINX Reverse Proxy -> WSGI -> Python/Flask Backend](https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask#nginx-reverse-proxy---wsgi---pythonflask-backend)
