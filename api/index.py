from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime, timedelta
from data.database import DataBase
# from mangum import Mangum
# import uvicorn

load_dotenv()
db = DataBase()
app = FastAPI()
def parse_query_dates(request: Request):
    now = datetime.now()
    end_date_str = request.query_params.get("end_date")
    start_date_str = request.query_params.get("start_date")

    try:
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else now
    except ValueError:
        end_date = now

    try:
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else (now - timedelta(days=7))
    except ValueError:
        start_date = now - timedelta(days=7)

    return start_date, end_date


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "https://trout-tracker-wa.vercel.app"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def index_view():
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
    return api_info


@app.get("/stocked_lakes_data")
async def get_stocked_lakes_data(request: Request):
    start_date, end_date =  parse_query_dates(request)
    if start_date and end_date:
        stocked_lakes = db.get_stocked_lakes_data(
            end_date=end_date, start_date=start_date)

        return stocked_lakes


@app.get("/total_stocked_by_date_data")
async def get_total_stocked_by_date_data(request: Request):
    start_date, end_date =  parse_query_dates(request)
    if start_date and end_date:
        total_stocked_by_date = db.get_total_stocked_by_date_data(
            start_date=start_date, end_date=end_date)

        total_stocked_by_date = [{"date": str(date), "stocked_fish": stocked_fish}
                                for date, stocked_fish in total_stocked_by_date]

        return total_stocked_by_date


@app.get("/hatchery_totals")
async def get_hatchery_totals(request: Request):
    start_date, end_date = parse_query_dates(request)
    if start_date and end_date:
        print("START AND FUCKING END DATE!!!!",start_date,end_date)
        hatchery_totals = db.get_hatchery_totals(
            start_date=start_date, end_date=end_date)
        hatchery_totals = [{'hatchery': row[0], 'sum_1': row[1]}
                        for row in hatchery_totals]
        return hatchery_totals


@app.get("/derby_lakes_data")
async def get_derby_lakes_data():
    derby_lakes = db.get_derby_lakes_data()
    derby_lakes = [dict(row) for row in derby_lakes]
    return derby_lakes


@app.get("/date_data_updated")
async def get_date_data_updated():
    last_updated = db.get_date_data_updated()
    last_updated = str(last_updated)
    return last_updated


@app.get("/hatchery_names")
async def get_unique_hatcheries():
    unique_hatcheries = db.get_unique_hatcheries()
    return unique_hatcheries


# handler = Mangum(app) 

# if __name__ == "__main__":
#   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)