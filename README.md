# Washington Trout Stats

**Author:** Thomas Basham

[trout-finder.vercel.app](https://trout-finder.vercel.app)

![Python application](https://img.shields.io/badge/Flask-23daaf?style=for-the-badge&logo=flask&logoColor=white)
![Python application](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python application](https://img.shields.io/badge/Vercel-000?style=for-the-badge&logo=Vercel&logoColor=white)

[![Python application](https://github.com/Thomas-Basham/trout-finder/actions/workflows/python-app.yml/badge.svg)](https://github.com/Thomas-Basham/trout-finder/actions/workflows/python-app.yml)

[![daily-cron](https://github.com/Thomas-Basham/trout-finder/actions/workflows/cron.yaml/badge.svg)](https://github.com/Thomas-Basham/trout-finder/actions/workflows/cron.yaml)

A Flask Web App used for displaying the most recent lakes that were stocked with trout in Washington State on an
interactive map

## Problem Domain

The [Washington Department of Fish and Wildlife Trout Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants) is excellent if you want to view data from clunky tables with endless amounts of pages to click through. That equates to one request for each page click, multiplied by an unanticipated amount of users, creates an unnecessary amount of web traffic that inevitably costs we the taxpayers more money. What if we had all of this data in one place, where a single computer could connect to the [WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants) each day and provide all of the data they need in one convenient page, offloading the WDFW's bandwidth at the same time?

## Tech Used

- Flask

- Beautiful Soup (Data scraped from [WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants))

- Folium

- SQLAlchemy

- Postgres Database

- Cron Job(To schedule webscraping daily)

- Google V3 Geolocator(To get lat/lon of lakes)

<!-- ## Get started Contributing -->

<!-- - Fork this repository
- Clone to your machine
- Open in IDE
- Create a Python virtual environment
- Run these CLI commands:

      pip install -r back_end/requirements.txt

      pip install -r front_end/requirements.txt

- To run development server:

         python front_end/wsgi.py -->

Or With Docker:

      docker-compose build
      docker-compose up -d
      

## Resources

[WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants)

[SqAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)

![Washington Trout Stats Screenshot](screenshot.webp)
