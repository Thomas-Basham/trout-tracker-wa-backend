# main.py
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.database import DataBase
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__.split('.')[0])
app.app_context().push()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all domains
db = DataBase()


@app.route('/', methods=['GET'])
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


@app.route('/stocked_lakes_data', methods=['GET'])
def get_stocked_lakes_data():
    now = datetime.now()

    end_date = request.args.get('end_date', default=now)

    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    stocked_lakes = db.get_stocked_lakes_data(start_date, end_date)
    stocked_lakes_dicts = [stocked_lake.to_dict()
                           for stocked_lake in stocked_lakes]

    return jsonify(stocked_lakes_dicts)


@app.route('/total_stocked_by_date_data', methods=['GET'])
def get_total_stocked_by_date_data():
    now = datetime.now()

    end_date = request.args.get('end_date', default=now)

    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    total_stocked_by_date = db.get_total_stocked_by_date_data(
        start_date, end_date)

    # Convert to a list of dictionaries
    total_stocked_by_date = [{"date": str(date), "stocked_fish": stocked_fish}
                             for date, stocked_fish in total_stocked_by_date]

    return jsonify(total_stocked_by_date)


@app.route('/hatchery_totals', methods=['GET'])
def get_hatchery_totals():

    now = datetime.now()

    end_date = request.args.get('end_date', default=now)

    start_date = request.args.get(
        'start_date', default=now - timedelta(days=7))

    hatchery_totals = db.get_hatchery_totals(start_date, end_date)
    hatchery_totals = [{'hatchery': row[0], 'sum_1': row[1]}
                       for row in hatchery_totals]
    return jsonify(hatchery_totals)


@app.route('/derby_lakes_data', methods=['GET'])
def get_derby_lakes_data():
    derby_lakes = db.get_derby_lakes_data()
    derby_lakes = [dict(row) for row in derby_lakes]
    return jsonify(derby_lakes)


@app.route('/date_data_updated', methods=['GET'])
def get_date_data_updated():
    last_updated = db.get_date_data_updated()
    last_updated = str(last_updated)
    return jsonify(last_updated)


@app.route('/hatchery_names', methods=['GET'])
def get_unique_hatcheries():
    unique_hatcheries = db.get_unique_hatcheries()
    return jsonify(unique_hatcheries)
