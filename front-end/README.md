# Trout Finder

**Author:** Thomas Basham

[trout-finder.vercel.app](https://trout-finder.vercel.app)

![Python application](https://img.shields.io/badge/Flask-23daaf?style=for-the-badge&logo=flask&logoColor=white)
![Python application](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python application](    https://img.shields.io/badge/Vercel-000?style=for-the-badge&logo=Vercel&logoColor=white)

[![Python application](https://github.com/Thomas-Basham/trout-finder/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Thomas-Basham/trout-finder/actions/workflows/python-app.yml)

[![daily-cron](https://github.com/Thomas-Basham/trout-finder/actions/workflows/cron.yaml/badge.svg)](https://github.com/Thomas-Basham/trout-finder/actions/workflows/cron.yaml)

A Flask Web App used for displaying the most recent lakes that were stocked with trout in Washington State on an
interactive map

## Tech Used

* Flask

* Beautiful Soup (Data scraped from [WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants))

* Folium

* SQLAlchemy

* Postgres Database

* Cron Job(To schedule webscraping daily)

* Google V3 Geolocator(To get lat/lon of lakes)

[//]: # (![screenshot]&#40;static/screenshots/WaStockedTroutLakes1.png&#41;)

[//]: # (![screenshot]&#40;static/screenshots/WaStockedTroutLakes2.png&#41;)

[//]: # (![screenshot]&#40;static/screenshots/WaStockedTroutLakes3.png&#41;)

[//]: # (![screenshot]&#40;static/screenshots/WaStockedTroutLakes4.png&#41;)

[//]: # (![screenshot]&#40;static/screenshots/WaStockedTroutLakes5.png&#41;)

## Resources

[WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants)

[SqAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)
