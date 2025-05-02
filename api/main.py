# main.py
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.database import DataBase
from datetime import datetime, timedelta
from flask_cors import cross_origin

load_dotenv()
db = DataBase()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},
     origins=["http://localhost:3000", "https://trout-tracker-wa.vercel.app"], supports_credentials=True)
app.app_context().push()


@app.route('/', methods=['GET', 'OPTIONS'])
def index_view():
    api_info = {
        "message": "Welcome to the TroutTracker WA API",
        "routes": {
            "/": "API Information",
            "/stocked_lakes_data": "Retrieve data for stocked lakes",
            "/total_stocked_by_date_data": "Retrieve total number of fish stocked by date",
            "/hatchery_totals": "Retrieve hatchery totals",
            "/derby_lakes_data": "Retrieve derby lakes data",
            "/date_data_updated": "Retrieve the date when data was last updated"
        },
        "usage": {
            "/stocked_lakes_data": {
                "method": "GET",
                "params": {
                    "start_date": "Start date for data (optional, default: 7 days ago)",
                    "end_date": "End date for data (optional, default: current date)"
                },
                "example": "/stocked_lakes_data?start_date=2023-01-01&end_date=2023-01-07"
            },
            "/total_stocked_by_date_data": {
                "method": "GET",
                "params": {
                    "start_date": "Start date for data (optional, default: 7 days ago)",
                    "end_date": "End date for data (optional, default: current date)"
                },
                "example": "/total_stocked_by_date_data?start_date=2023-01-01&end_date=2023-01-07"
            },
            "/hatchery_totals": {
                "method": "GET",
                "params": {
                    "start_date": "Start date for data (optional, default: 7 days ago)",
                    "end_date": "End date for data (optional, default: current date)"
                },
                "example": "/hatchery_totals?start_date=2023-01-01&end_date=2023-01-07"
            },
            "/derby_lakes_data": {
                "method": "GET",
                "description": "Retrieve data for derby lakes",
                "example": "/derby_lakes_data"
            },
            "/date_data_updated": {
                "method": "GET",
                "description": "Retrieve the date when the data was last updated",
                "example": "/date_data_updated"
            }
        }
    }
    return jsonify(api_info)


@app.route('/stocked_lakes_data', methods=['GET', 'OPTIONS'])
def get_stocked_lakes_data():
    now = datetime.now()
    end_date = request.args.get('end_date', default=now)
    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    # Load with joined FK so water_location is eager-loaded
    stocked_lakes = db.get_stocked_lakes_data(
        end_date=end_date, start_date=start_date)

    return jsonify(stocked_lakes)


@app.route('/total_stocked_by_date_data', methods=['GET', 'OPTIONS'])
def get_total_stocked_by_date_data():
    now = datetime.now()

    end_date = request.args.get('end_date', default=now)

    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    total_stocked_by_date = db.get_total_stocked_by_date_data(
        start_date=start_date, end_date=end_date)

    # Convert to a list of dictionaries
    total_stocked_by_date = [{"date": str(date), "stocked_fish": stocked_fish}
                             for date, stocked_fish in total_stocked_by_date]

    return jsonify(total_stocked_by_date)


@app.route('/hatchery_totals', methods=['GET', 'OPTIONS'])
def get_hatchery_totals():

    now = datetime.now()

    end_date = request.args.get('end_date', default=now)

    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    hatchery_totals = db.get_hatchery_totals(
        start_date=start_date, end_date=end_date)
    hatchery_totals = [{'hatchery': row[0], 'sum_1': row[1]}
                       for row in hatchery_totals]
    return jsonify(hatchery_totals)


@app.route('/derby_lakes_data', methods=['GET', 'OPTIONS'])
def get_derby_lakes_data():
    derby_lakes = db.get_derby_lakes_data()
    derby_lakes = [dict(row) for row in derby_lakes]
    return jsonify(derby_lakes)


@app.route('/date_data_updated', methods=['GET', 'OPTIONS'])
def get_date_data_updated():
    last_updated = db.get_date_data_updated()
    last_updated = str(last_updated)
    return jsonify(last_updated)


@app.route('/hatchery_names', methods=['GET', 'OPTIONS'])
def get_unique_hatcheries():
    unique_hatcheries = db.get_unique_hatcheries()
    return jsonify(unique_hatcheries)
