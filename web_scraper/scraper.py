# from geopy.geocoders import Nominatim
import os
import re
from time import time
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from geopy import GoogleV3
from dotenv import load_dotenv

from api.database import DataBase, StockedLakes, WaterLocations


class Scraper:
    """
    ************************* Scrape data to render the map from *************************

    Need: Lake names, stock count, date stocked, derby participant, and lat/lon
    Steps:
    1. Scrape the data from wdfw.wa.gov
    2. Use Geolocator to get lat/lon
    3. Make the data into a list of dictionaries
    """

    def __init__(self, request_url=""):
        self.request_url = request_url
        self.response = {}
        self.soup = {}
        self.df = []  # List[Dict[str, Any]]

    def set_scraper_config(self, url=""):
        if not self.request_url:
            self.request_url = url
        self.response = get(self.request_url)
        if self.response.status_code != 200:
            print("Error fetching page")
            exit()
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def scrape_water_locations_initialize_df(self):
        found_text = self.soup.select('.views-field-lake-stocked')
        # abbreviations found in html table in wdfw site
        ABBREVIATIONS = {"LK": "Lake", "PD": "Pond",
                         "CR": "Creek", "PRK": "Park", "CO": "County"}

        # makes a tuple of (cleaned version, original version) from the abbreviations
        text_list = [
            (
                re.sub(
                    r"\(.*?\)|[^\w\s\d]|(?<!\w)(\d+)(?!\w)|\b(" +
                    "|".join(ABBREVIATIONS.keys()) + r")\b",
                    lambda m: "" if m.group(
                        1) else ABBREVIATIONS.get(m.group(2), ""),
                    i.text.strip() + " County"
                ).strip().replace("\n", "").replace(" Region ", "").replace("  ", " ").title(),
                i.text
            )
            for i in found_text
        ][1:]
        # Initialize df with placeholders
        self.df = [
            {
                "lake": clean,
                "original_html_name": orig,
                "stocked_fish": None,
                "date": None,
                "species": None,
                "weight": None,
                "hatchery": None,
                "latitude": None,
                "longitude": None,
                "directions": None,
                "derby_participant": False
            }
            for clean, orig in text_list
        ]

    # return list of Stock Counts
    def scrape_stock_count(self):
        found_stock_counts = self.soup.findAll(
            class_="views-field views-field-num-fish")

        stock_count_text_list = [i.text.strip().replace(',', '')
                                 for i in found_stock_counts]

        stock_count_int_list = []
        for i in stock_count_text_list:
            try:
                stock_count_int_list.append(int(i))
            except ValueError:
                stock_count_int_list.append(i)
                print(f"Error: {i} is not a valid number")
                continue

        counts = stock_count_int_list[1:]
        for i, cnt in enumerate(counts):
            if i < len(self.df):
                self.df[i]['stocked_fish'] = cnt

    # return list of Species
    def scrape_species(self):
        found_text = self.soup.findAll(
            class_="views-field views-field-species")

        species_text_list = [i.text.strip() for i in found_text]

        species_list = species_text_list[1:]
        for i, sp in enumerate(species_list):
            if i < len(self.df):
                self.df[i]['species'] = sp

    # return list of Weights
    def scrape_weights(self):
        found_text = self.soup.findAll(
            class_="views-field views-field-fish-per-lb")

        weights_float_list = []
        for i in found_text:
            try:
                weight = float(i.text.strip())
                weights_float_list.append(weight)
            except ValueError:
                # handle the error here, such as skipping the value or setting it to a default value
                print(f"Could not convert {i.text.strip()} to float")
        for i, w in enumerate(weights_float_list):
            if i < len(self.df):
                self.df[i]['weight'] = w

    # return list of Weights
    def scrape_hatcheries(self):
        found_text = self.soup.findAll(
            class_="views-field views-field-hatchery")

        hatcheries_text_list = [i.text.strip().title() for i in found_text]

        hatchery_list = hatcheries_text_list[1:]
        for i, h in enumerate(hatchery_list):
            if i < len(self.df):
                self.df[i]['hatchery'] = h

    # Return list of Scraped Dates
    def scrape_date(self):
        date_text = self.soup.findAll(
            class_="views-field views-field-stock-date")

        date_text_list = [i.text.strip() for i in date_text]

        date_list = []
        for i in date_text_list:
            try:
                date_list.append(datetime.strptime(i, '%b %d, %Y').date(
                ) or datetime.strptime(i, '%b %dd, %Y').date())
            except ValueError:
                date_list.append(i)
                print(f"Error: {i} is not a valid date")
                continue

        dates = date_list[1:]
        for i, d in enumerate(dates):
            if i < len(self.df):
                self.df[i]['date'] = d

    # Return a list of names of lakes that are in the state trout derby
    # TODO: Update this. Not working at the moment
    def scrape_derby_names(self):

        # The trout derby doesn't start until april 22. don't scrape names unless the derby is running
        Trout_derby_start_date = datetime(2024, 4, 30)
        today = datetime.now()
        if today > Trout_derby_start_date:
            url_string = "https://wdfw.wa.gov/fishing/contests/trout-derby/lakes"

            # Reassign response and soup to new url
            self.response = get(url_string)
            self.soup = BeautifulSoup(self.response.content, "html.parser")

            # Scrape Names
            text_list = []
            found_text = self.soup.find("div", {"class": "derby-lakes-list"})
            if found_text:
                found_text = found_text.findAll("ul", recursive=False)

                for i in found_text:
                    text_list.append(i.find("li").text)

                # Clean up Names
                text_lst_trimmed = []
                for i in text_list:
                    text_lst_trimmed.append(i.replace("\n", ""))
                derby_list = [
                    re.sub(r"\(.*?\)", '', text).title() for text in text_lst_trimmed]
                for row in self.df:
                    if row['lake'] in derby_list:
                        row['derby_participant'] = True
                # add to df to make it  {stocking_reports: [], derby_waters: []}
            else:
                print("No derby lake names")
                return

    def get_lat_lon(self):
        locator = GoogleV3(api_key=os.getenv('GV3_API_KEY'))

        for stock_report_object in self.df:
            water_location = data_base.get_water_location(
                stock_report_object['original_html_name']
            )

            if water_location and data_base.record_exists(
                StockedLakes,
                water_location_id=water_location.id,
                stocked_fish=stock_report_object['stocked_fish'],
                date=stock_report_object['date']
            ):
                print(
                    f"Skipped In the scraper. already added {stock_report_object['original_html_name']} "
                    f"{stock_report_object['stocked_fish']} {stock_report_object['date']}"
                )
                continue

            # Geocode and update in place
            geocode = locator.geocode(
                stock_report_object["lake"] + " washington state"
            )
            if geocode:
                print(f"Geocoding {stock_report_object['lake']}")
                stock_report_object['latitude'] = float(geocode.point[0])
                stock_report_object['longitude'] = float(geocode.point[1])
            else:
                stock_report_object['latitude'] = 0.0
                stock_report_object['longitude'] = 0.0

            stock_report_object['directions'] = (
                f"https://www.google.com/maps/search/?api=1&query={stock_report_object['lake']}"
            )

    def run_all_scrapes(self):
        self.scrape_water_locations_initialize_df()
        self.scrape_stock_count()
        self.scrape_date()
        self.scrape_species()
        self.scrape_weights()
        self.scrape_hatcheries()
        # self.scrape_derby_names()
        self.get_lat_lon()
        # print("DF AFTER SCRAPING: ", self.df)
        return self.df


def write_archived_data():
    # ran only in a dev environment, used to get all the wdfw trout plant archives
    # data_base = DataBase()
    print("archiving....")
    scraper = Scraper()
    # for i in range(2015, 2024):  # data goes back to 2015
    for j in range(8):  # there are at most 7 pages to scrape

        # print("scraping....year {i}, page {j}")
        scraper.set_scraper_config(
            f"https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/archive/2020?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250&page={j}"
            # f'https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/archive/{i}?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250&page={j}'
            # f'https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250&page={j}'
        )
        scraper.scrape_water_locations_initialize_df()
        [data_base.insert_water_location(
            original_html_name=lake_name[1], water_name_cleaned=lake_name[0], latitude=0.0, longitude=0.0, directions="", derby_participant=False) for lake_name in scraper.df]
        # print(f'updated year {i}, page {j}')


# Run Once Every day
if __name__ == "__main__":
    load_dotenv()
    start_time = time()
    data_base = DataBase()

    scraper = Scraper(
        request_url="https://wdfw.wa.gov/fishing/reports/stocking/trout-plants/all?lake_stocked=&county=&species=&hatchery=&region=&items_per_page=250")
    scraper.set_scraper_config()
    scraper.run_all_scrapes()
    data_base.write_data(data=scraper.df)

    # if os.getenv('ENVIRONMENT') and os.getenv('ENVIRONMENT') == 'testing':
    #     data_base.back_up_database()

    end_time = time()
    print(f"It took {end_time - start_time:.2f} seconds to compute")
