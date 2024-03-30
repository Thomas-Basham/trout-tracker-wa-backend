# Trout Tracker WA Backend

**Authors:** Thomas Basham

**Version:** 4.1.1

[trout-tracker-wa-backend.vercel.app](https://trout-tracker-wa-backend.vercel.app/)

[Front End Code](https://github.com/Thomas-Basham/trout-tracker-wa)

![Flask](https://img.shields.io/badge/Flask-23daaf?style=for-the-badge&logo=flask&logoColor=white)
![Postgresql](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000?style=for-the-badge&logo=Vercel&logoColor=white)

[![Python application](https://github.com/Thomas-Basham/washington-trout-stats/actions/workflows/python-app.yml/badge.svg)](https://github.com/Thomas-Basham/washington-trout-stats/actions/workflows/python-app.yml)

[![daily-cron](https://github.com/Thomas-Basham/washington-trout-stats/actions/workflows/cron.yaml/badge.svg)](https://github.com/Thomas-Basham/washington-trout-stats/actions/workflows/cron.yaml)

## Introduction

Trout Tracker WA is a comprehensive web application designed to provide updated information about trout stocking in Washington state. This repository contains all the essential backend components of the project, including database management, a Flask API and a web scraper.

### Getting Started

- [With WebScraper](./web_scraper/README.md)
- [With API](./api/README.md)

### Features

- Flask backend for server and API management.
- Data scraping tool for fetching real-time data.
- Comprehensive API for data retrieval.

### Configuration

- Set environment variables in a `.env` file as required.
- Configure the database settings in the respective configuration files.

### Running the Application

Start the Flask server:

```bash
python main.py
```

### Contributions

- [Get started Contributing](./CONTRIBUTING.md)

### Tech Used

- Flask

- Beautiful Soup (Data scraped from [WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants))

- Folium

- SQLAlchemy

- PostgreSQL Database

- [GitHub Cron Job](https://github.com/Thomas-Basham/washington-trout-stats/actions/workflows/cron.yaml) (To schedule webscraping daily)

- Google Geolocation API (To get lat/lon of lakes)

- Docker

## Resources

[WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants)

[Flask](https://flask.palletsprojects.com/)

[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

[SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)

[Docker and NGINX](https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask)

[Google Geolocator API](https://developers.google.com/maps/documentation/geolocation/overview)

### Contact

- Developer: Thomas Basham
- Email: bashamtg@gmail.com
