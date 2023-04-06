from dotenv import load_dotenv
from flask import Flask, render_template, request
from data_base import DataBase
from map_and_charts import make_map, show_total_stocked_by_date_chart, show_total_stocked_by_hatchery_chart
from time import time

load_dotenv()
app = Flask(__name__.split('.')[0])
app.app_context().push()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route('/', methods=['GET', 'POST'])
def index_view():
  data_base = DataBase()
  days = 365

  if request.method == 'POST':
    form = request.form
    days = int(form['days'])

  # DATA QUERIES
  filtered_lakes_by_days = data_base.get_stocked_lakes_data(days=days)
  filtered_total_stocked_by_date = data_base.get_total_stocked_by_date_data(days=days)
  filtered_total_stocked_by_hatchery = data_base.get_hatchery_totals(days=days)
  date_data_updated = data_base.get_date_data_updated()
  derby_lakes_data = data_base.get_derby_lakes_data()

  # MAP AND CHARTS
  folium_map = make_map(filtered_lakes_by_days)
  total_stocked_by_date_chart = show_total_stocked_by_date_chart(filtered_total_stocked_by_date)
  total_stocked_by_hatchery_chart = show_total_stocked_by_hatchery_chart(filtered_total_stocked_by_hatchery)
  most_recent_stocked = filtered_lakes_by_days

  return render_template('index.html', folium_map=folium_map, total_stocked_by_date_chart=total_stocked_by_date_chart,
                         total_stocked_by_hatchery_chart=total_stocked_by_hatchery_chart,
                         derby_lakes=derby_lakes_data, most_recent_stocked=most_recent_stocked, days=days,
                         date_data_updated=date_data_updated)
