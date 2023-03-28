from folium import Map, Popup, Icon, Marker, raster_layers, LayerControl
from folium.plugins import MarkerCluster, Fullscreen
import json


# Make the Map with Folium
def make_map(lakes):
  if lakes:
    latitudes = [lake["latitude"] for lake in lakes if lake["latitude"] != 0.0]
    longitudes = [lake["longitude"] for lake in lakes if lake["longitude"] != 0.0]

    location = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]
    folium_map = Map(width="100%", height="100%", max_width="100%", min_height="100%", location=location,
                     allowFullScreen="True",
                     zoom_start=7, tiles="Stamen Terrain")

    marker_cluster = MarkerCluster().add_to(folium_map)
    Fullscreen(
      position='topright',
      title='Expand me',
      title_cancel='Exit me',
      force_separate_button=False
    ).add_to(folium_map)

    for lake in lakes:
      if lake["latitude"] != 0.0:
        html = f'''
          <h5 >{lake["lake"]}</h5>
          <p style="color:red">Date Stocked: {lake["date"]}</p>
          <p style="color:green">Stocked Amount: {lake["stocked_fish"]}</p>
          <p style="color:cyan">Species: {lake["species"]}</p>
          <p style="color:orange">Hatchery: {lake["hatchery"]}</p>
          <a style="color:blue" href="{lake["directions"]}" target="_blank">Directions via Googlemaps </a>
          '''

        popup = Popup(html, max_width=400, lazy=True)
        location = (lake["latitude"], lake["longitude"])

        if lake["derby_participant"]:
          Marker(location=location, tooltip=lake["lake"], popup=popup,
                 icon=Icon(color='red', icon='trophy', prefix='fa')).add_to(
            folium_map)
        else:
          Marker(location=location, tooltip=lake["lake"], popup=popup,
                 icon=Icon(color='blue', icon='info', prefix='fa')).add_to(
            marker_cluster)
    raster_layers.TileLayer('OpenStreetMap').add_to(folium_map)
    LayerControl().add_to(folium_map)

    return folium_map._repr_html_()
  else:
    # return a blank map if there is no data
    return Map(location=[47.7511, -120.7401], zoom_start=7)._repr_html_()


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
        }
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
        }
      }
    }
    chart_data_json = json.dumps(chart_data)
    chart_options_json = json.dumps(chart_options)
    graph_html = f'<canvas id="total-stocked-by-hatchery-chart"></canvas>\n<script>\nvar ctx = document.getElementById("total-stocked-by-hatchery-chart").getContext("2d");\nvar myChart = new Chart(ctx, {{ type: "bar", data: {chart_data_json}, options: {chart_options_json} }});\n</script>'
    return graph_html
  else:
    return f'<canvas id="total-stocked-by-hatchery-chart"></canvas>'
