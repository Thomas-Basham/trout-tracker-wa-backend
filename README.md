# wa-stocked-trout-finder
[Deployed Site](https://wa-stocked-trout-finder.herokuapp.com/)

A Full Stack Flask Web App used for visually displaying the most recent lakes that were stocked with trout in Washington State 

Data scraped from WDFW.wa.gov website with Beautiful Soup

put into a Pandas Dataframe

Fed to Folium to render the map

Data persisted with Heroku Postgres

Chron Job set to scrape WDFW and update with new data every night at 2:00am



## Resources
[WDFW Stock Report](https://wdfw.wa.gov/fishing/reports/stocking/trout-plants)

[SqAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)

[Pandas to SQL](https://towardsdatascience.com/upload-your-pandas-dataframe-to-your-database-10x-faster-eb6dc6609ddf)
