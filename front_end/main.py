import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from flask import Flask, render_template, request
from folium import Map, Popup, Icon, Marker, raster_layers, LayerControl
from folium.plugins import MarkerCluster, Fullscreen
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, text, desc
from data_tables import StockedLakes, DerbyLake, Utility

load_dotenv()
app = Flask(__name__.split('.')[0])
app.app_context().push()

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


class DataBase:
  def __init__(self):
    # Load Database
    if os.getenv("SQLALCHEMY_DATABASE_URI"):
      self.engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    else:
      self.engine = create_engine('sqlite:///')

    self.conn = self.engine.connect()
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

    self.end_date = datetime.now()
    self.start_date = self.end_date - timedelta(days=365)

  def get_stocked_lakes_data(self):
    stocked_lakes = self.session.query(
      StockedLakes.date,
      StockedLakes.lake,
      StockedLakes.stocked_fish,
      StockedLakes.species,
      StockedLakes.hatchery,
      StockedLakes.weight,
      StockedLakes.latitude,
      StockedLakes.longitude,
      StockedLakes.directions,
      StockedLakes.derby_participant
    ).filter(
      StockedLakes.date.between(self.start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()
    return stocked_lakes

  def get_hatchery_totals(self):
    hatchery_totals = data_base.session.query(
      StockedLakes.hatchery,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.hatchery).filter(
      StockedLakes.date.between(self.start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(desc(text('sum_1'))).all()
    return hatchery_totals

  def get_derby_lakes_data(self):
    derby_lakes = self.conn.execute(text("SELECT * FROM derby_lakes_table")).fetchall()
    return derby_lakes

  def get_total_stocked_by_date_data(self):
    total_stocked_by_date = self.session.query(
      StockedLakes.date,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.date).filter(
      StockedLakes.date.between(self.start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()
    return total_stocked_by_date

  def get_date_data_updated(self):
    last_updated = self.session.query(Utility).order_by(Utility.id.desc()).first()
    return last_updated.updated


data_base = DataBase()
stocked_lakes_data = data_base.get_stocked_lakes_data()
derby_lakes_data = data_base.get_derby_lakes_data()
total_stocked_by_date_data = data_base.get_total_stocked_by_date_data()
total_stocked_by_hatchery_data = data_base.get_hatchery_totals()
date_data_updated = data_base.get_date_data_updated()


@app.route('/', methods=['GET', 'POST'])
def index_view():
  global data_base, stocked_lakes_data, derby_lakes_data
  days = 365
  end_date = datetime.now()

  if request.method == 'POST':
    form = request.form
    days = int(form['days'])
    start_date = end_date - timedelta(days=days)

    # DATA QUERY
    filtered_lakes_by_days = data_base.session.query(
      StockedLakes.date,
      StockedLakes.lake,
      StockedLakes.stocked_fish,
      StockedLakes.species,
      StockedLakes.hatchery,
      StockedLakes.weight,
      StockedLakes.latitude,
      StockedLakes.longitude,
      StockedLakes.directions,
      StockedLakes.derby_participant
    ).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()

    # DATA QUERY
    filtered_total_stocked_by_date = data_base.session.query(
      StockedLakes.date,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.date).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()

    filtered_total_stocked_by_hatchery = data_base.session.query(
      StockedLakes.hatchery,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.hatchery).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y'))
    ).order_by(desc(text('sum_1'))).all()

    # MAP AND CHARTS
    folium_map = make_map(filtered_lakes_by_days)._repr_html_()

    total_stocked_by_date_chart = show_total_stocked_by_date_chart(filtered_total_stocked_by_date)

    total_stocked_by_hatchery_chart = show_total_stocked_by_hatchery_chart(filtered_total_stocked_by_hatchery)

    most_recent_stocked = filtered_lakes_by_days

  else:
    # if request.method == 'GET':

    total_stocked_by_date_chart = show_total_stocked_by_date_chart(total_stocked_by_date_data)

    total_stocked_by_hatchery_chart = show_total_stocked_by_hatchery_chart(total_stocked_by_hatchery_data)

    folium_map = make_map(stocked_lakes_data)._repr_html_()

    most_recent_stocked = stocked_lakes_data

  return render_template('index.html', folium_map=folium_map, total_stocked_by_date_chart=total_stocked_by_date_chart,
                         total_stocked_by_hatchery_chart=total_stocked_by_hatchery_chart,
                         derby_lakes=derby_lakes_data, most_recent_stocked=most_recent_stocked, days=days,
                         date_data_updated=date_data_updated)


@app.route('/fullscreen')
def map_full_screen_view():
  global stocked_lakes_data
  folium_map = make_map(stocked_lakes_data)._repr_html_()

  return render_template('map_full_screen.html', folium_map=folium_map)


# *********************** DRIVER FOR MAP DATA **********************************
# Make the Map with Folium
def make_map(lakes):
  if lakes:
    latitudes = [lake["latitude"] for lake in lakes]
    longitudes = [lake["longitude"] for lake in lakes]

    location = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]
    folium_map = Map(width="100%", max_width="100%", max_height="100%", location=location, zoom_start=7)

    marker_cluster = MarkerCluster().add_to(folium_map)
    Fullscreen(
      position='topright',
      title='Expand me',
      title_cancel='Exit me',
      force_separate_button=False
    ).add_to(folium_map)

    for lake in lakes:
      html = f'''
        <h3 >{lake["lake"].title()}<h3/>
        <p style="color:red">Date Stocked: {lake["date"]}</p>
        <p style="color:green">Stocked Amount: {lake["stocked_fish"]}<p/>
        <a style="color:blue" href="{lake["directions"]}" target="_blank">Directions via Googlemaps <a/>
        '''

      popup = Popup(html, max_width=400)
      location = (lake["latitude"], lake["longitude"])

      if lake["derby_participant"]:
        Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
               icon=Icon(color='red', icon='trophy', prefix='fa')).add_to(
          folium_map)
      else:
        Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
               icon=Icon(color='blue', icon='info', prefix='fa')).add_to(
          marker_cluster)

    raster_layers.TileLayer('Stamen Terrain').add_to(folium_map)
    LayerControl().add_to(folium_map)

    return folium_map
  else:
    # return a blank map if there is no data
    return Map(location=[47.7511, -120.7401], zoom_start=7)


def show_total_stocked_by_date_chart(lakes):
  if lakes:
    date_format = '%Y-%m-%d'
    dates, total_stocked_fish = zip(*lakes)
    date_strings = [date.strftime(date_format) for date in dates]
    chart_data = {
      'labels': date_strings,
      'datasets': [
        {
          'label': 'Total Stocked Trout by Date',
          'data': total_stocked_fish,
          'backgroundColor': '#9fd3c7',
          'borderColor': '#9fd3c7',
          'color': '#9fd3c7',
          'borderWidth': 1,
          'pointRadius': 2
        }
      ]
    }
    chart_options = {
      'scales': {
        'y': {
          'ticks': {'color': '#ececec', 'beginAtZero': True}
        },
        'x': {
          'ticks': {'color': '#ececec'}
        },
        'xAxes': [{
          'type': 'time',
          'time': {
            'unit': 'day',
            'parser': date_format,
            'tooltipFormat': 'll'
          }
        }]
      }
    }
    chart_data_json = json.dumps(chart_data)
    chart_options_json = json.dumps(chart_options)
    graph_html = f'<canvas id="total-stocked-by-date-chart"></canvas>\n<script>\nvar ctx = document.getElementById("total-stocked-by-date-chart").getContext("2d");\nvar myChart = new Chart(ctx, {{ type: "line", data: {chart_data_json}, options: {chart_options_json} }});\n</script>'
    return graph_html
  else:
    return f'<canvas id="total-stocked-by-date-chart">NO DATA</canvas>'


def show_total_stocked_by_hatchery_chart(lakes):
  if lakes:
    hatcheries, total_stocked_fish = zip(*lakes)
    chart_data = {
      'labels': hatcheries,
      'datasets': [
        {
          'label': 'Total Stocked Trout by Hatchery',
          'data': total_stocked_fish,
          'color': '#ececec',
          'borderColor': '#9fd3c7',
          'backgroundColor': '#9fd3c7',
          'borderWidth': 1,
          'pointRadius': 3
        }
      ]
    }
    chart_options = {
      'scales': {
        'y': {
          'ticks': {'color': '#ececec', 'beginAtZero': True}
        },
        'x': {
          'ticks': {'color': '#ececec'}
        },
        'color': '#ececec',
        'tickColor': '#ececec',
        'xAxes': [{
          'type': 'text',
        }]
      }
    }
    chart_data_json = json.dumps(chart_data)
    chart_options_json = json.dumps(chart_options)
    graph_html = f'<canvas id="total-stocked-by-hatchery-chart"></canvas>\n<script>\nvar ctx = document.getElementById("total-stocked-by-hatchery-chart").getContext("2d");\nvar myChart = new Chart(ctx, {{ type: "bar", data: {chart_data_json}, options: {chart_options_json} }});\n</script>'
    return graph_html
  else:
    return f'<canvas id="total-stocked-by-hatchery-chart"></canvas>'
