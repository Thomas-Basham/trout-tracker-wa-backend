import folium
from folium.plugins import MarkerCluster, Fullscreen
from flask import Flask, render_template, request
from sqlalchemy import func
from dotenv import load_dotenv
import sys
import logging
from scraper import DataBase, StockedLakes
from plotly.offline import plot
import plotly.graph_objs as go
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__.split('.')[0])
app.app_context().push()
data_base = DataBase()
data = data_base.get_data()  # returns data object
stocked_lakes_data = data['stocked_lakes']
derby_lakes_data = data['derby_lakes']
total_stocked_by_date = data['total_stocked_by_date']

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


@app.route('/', methods=['GET', 'POST'])
def index_view():
  global data_base, data, stocked_lakes_data, derby_lakes_data, total_stocked_by_date

  days = 30
  if len(stocked_lakes_data) > 1:
    folium_map = make_map(stocked_lakes_data)._repr_html_()

    derby_lakes_set = set(lake["lake"] for lake in derby_lakes_data)
  else:
    data_base.write_data()
    data = data_base.get_data()  # returns data object
    stocked_lakes_data = data['stocked_lakes']
    derby_lakes_data = data['derby_lakes']
    derby_lakes = derby_lakes_data
    folium_map = make_map(stocked_lakes_data)._repr_html_()

    derby_lakes_set = set(lake["lake"] for lake in derby_lakes)

  chart = show_chart(total_stocked_by_date)

  if request.method == 'POST':
    form = request.form
    days = int(form['days'])
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    filtered_lakes_by_days = data_base.session.query(
      StockedLakes.date,
      StockedLakes.lake,
      StockedLakes.stocked_fish,
      StockedLakes.latitude,
      StockedLakes.longitude,
      StockedLakes.directions,
      StockedLakes.derby_participant
    ).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()

    folium_map = make_map(filtered_lakes_by_days)._repr_html_()

    filtered_total_stocked_by_date = data_base.session.query(
      StockedLakes.date,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.date).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()
    chart = show_chart(filtered_total_stocked_by_date)

  return render_template('index.html', folium_map=folium_map, chart=chart,
                         derby_lakes=derby_lakes_set, most_recent_stocked=stocked_lakes_data, days=days)


@app.route('/fullscreen')
def map_full_screen_view():
  global data_base, stocked_lakes_data, data
  if len(stocked_lakes_data) > 1:
    folium_map = make_map(stocked_lakes_data)._repr_html_()
  else:
    data_base.write_data()
    data = data_base.get_data()  # returns data object
    stocked_lakes_data = data['stocked_lakes']

    folium_map = make_map(stocked_lakes_data)._repr_html_()

  return render_template('map_full_screen.html', folium_map=folium_map)


# *********************** DRIVER FOR MAP DATA **********************************
# Make the Map with Folium
def make_map(lakes):
  if lakes:
    latitudes = [float(lake["latitude"]) for lake in lakes if lake != '']
    longitudes = [float(lake["longitude"]) for lake in lakes if lake != '']
    location = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]
    folium_map = folium.Map(width="100%", max_width="100%", max_height="100%", location=location, zoom_start=7)

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

      popup = folium.Popup(html, max_width=400)
      location = (lake["latitude"], lake["longitude"])

      if lake["derby_participant"]:
        folium.Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
                      icon=folium.Icon(color='red', icon='trophy', prefix='fa')).add_to(
          folium_map)
      else:
        folium.Marker(location=location, tooltip=lake["lake"].capitalize(), popup=popup,
                      icon=folium.Icon(color='blue', icon='info', prefix='fa')).add_to(
          marker_cluster)

    folium.raster_layers.TileLayer('Stamen Terrain').add_to(folium_map)
    folium.LayerControl().add_to(folium_map)

    return folium_map
  else:
    # return a blank map if there is no data
    return folium.Map(location=[47.7511, -120.7401], zoom_start=7)


def show_chart(lakes):
  # Extract the dates and total stocked fish into separate lists
  dates = [item[0] for item in lakes]
  total_stocked_fish = [item[1] for item in lakes]
  # print(dates)
  # Create a Plotly line graph with the total stocked fish by date
  data = go.Scatter(x=dates, y=total_stocked_fish, mode='lines')
  layout = go.Layout(title='Total Stocked Trout by Date',
                     xaxis_title='Date',
                     yaxis_title='Total Stocked Fish',
                     margin=dict(l=50, r=50, t=50, b=50),
                     autosize=True
                     )
  fig = go.Figure(data=[data], layout=layout)
  graph_html = plot(fig, output_type='div')

  return graph_html


app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if __name__ == '__main__':
  app.run(debug=False)
