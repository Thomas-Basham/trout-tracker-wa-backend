from front_end.data_base import DataBase
from time import time
from dotenv import load_dotenv
from map_and_charts import make_map, show_total_stocked_by_date_chart, show_total_stocked_by_hatchery_chart

load_dotenv()


def test_load_time():
  start_time = time()
  data_base = DataBase()
  days = 10
  stocked_lakes_data = data_base.get_stocked_lakes_data(days)

  total_stocked_by_hatchery_data = data_base.get_hatchery_totals(days)
  total_stocked_by_date_data = data_base.get_total_stocked_by_date_data(days)
  data_base.get_derby_lakes_data()
  data_base.get_date_data_updated()

  total_stocked_by_date_chart = show_total_stocked_by_date_chart(total_stocked_by_date_data)
  total_stocked_by_hatchery_chart = show_total_stocked_by_hatchery_chart(total_stocked_by_hatchery_data)
  # folium_map = make_map(data_base.get_stocked_lakes_data(days))
  end_time = time()
  print(f"It took {end_time - start_time:.2f} seconds to compute")
