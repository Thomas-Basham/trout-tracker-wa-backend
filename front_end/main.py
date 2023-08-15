from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from front_end.database import DataBase
from front_end.map_and_charts import make_map, show_total_stocked_by_date_chart, show_total_stocked_by_hatchery_chart
from time import time

load_dotenv()
app = Flask(__name__.split('.')[0])
app.app_context().push()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = DataBase()

@app.route('/', methods=['GET', 'POST'])
def index_view():
  days = 60

  if request.method == 'POST':
    form = request.form
    days = int(form['days'])

  # DATA QUERIES
  filtered_lakes_by_days = db.get_stocked_lakes_data(days=days)
  filtered_total_stocked_by_date = db.get_total_stocked_by_date_data(days=days)
  filtered_total_stocked_by_hatchery = db.get_hatchery_totals(days=days)
  date_data_updated = db.get_date_data_updated()
  derby_lakes_data = db.get_derby_lakes_data()

  # MAP AND CHARTS
  folium_map = make_map(filtered_lakes_by_days)
  total_stocked_by_date_chart = show_total_stocked_by_date_chart(filtered_total_stocked_by_date)
  total_stocked_by_hatchery_chart = show_total_stocked_by_hatchery_chart(filtered_total_stocked_by_hatchery)
  most_recent_stocked = filtered_lakes_by_days

  return render_template('index.html', folium_map=folium_map, total_stocked_by_date_chart=total_stocked_by_date_chart,
                         total_stocked_by_hatchery_chart=total_stocked_by_hatchery_chart,
                         derby_lakes=derby_lakes_data, most_recent_stocked=most_recent_stocked, days=days,
                         date_data_updated=date_data_updated)

# Route for retrieving stocked lakes data
@app.route('/stocked_lakes_data', methods=['GET'])
def get_stocked_lakes_data():
    days = int(request.args.get('days', default=30))
    stocked_lakes = db.get_stocked_lakes_data(days)
    print(stocked_lakes)
    stocked_lakes = [dict(row) for row in stocked_lakes]
    return jsonify(stocked_lakes)

# Route for retrieving hatchery totals
@app.route('/hatchery_totals', methods=['GET'])
def get_hatchery_totals():
    days = 365
    hatchery_totals = db.get_hatchery_totals(days)
    hatchery_totals = [{'hatchery': row[0], 'sum_1': row[1]} for row in hatchery_totals]
    return jsonify(hatchery_totals)

# Route for retrieving derby lakes data
@app.route('/derby_lakes_data', methods=['GET'])
def get_derby_lakes_data():
    derby_lakes = db.get_derby_lakes_data()
    derby_lakes = [dict(row) for row in derby_lakes]
    return jsonify(derby_lakes)

# Route for retrieving total stocked by date data
@app.route('/total_stocked_by_date_data', methods=['GET'])
def get_total_stocked_by_date_data():
    days = 365
    total_stocked_by_date = db.get_total_stocked_by_date_data(days)
    total_stocked_by_date = [(str(date), stocked_fish) for date, stocked_fish in total_stocked_by_date]
    return jsonify(total_stocked_by_date)

# Route for retrieving the date data was last updated
@app.route('/date_data_updated', methods=['GET'])
def get_date_data_updated():
    last_updated = db.get_date_data_updated()
    last_updated = str(last_updated)
    return jsonify(last_updated)

@app.route('/cache-me')
def cache():
	return "nginx will cache this response"

@app.route('/info')
def info():

	resp = {
		'connecting_ip': request.headers['X-Real-IP'],
		'proxy_ip': request.headers['X-Forwarded-For'],
		'host': request.headers['Host'],
		'user-agent': request.headers['User-Agent']
	}

	return jsonify(resp)

@app.route('/flask-health-check')
def flask_health_check():
	return "success"