from front_end.data_base import DataBase
from time import time
from dotenv import load_dotenv

load_dotenv()


def test_load_time():
  start_time = time()
  data_base = DataBase()
  days = 800

  stocked_lakes_data = data_base.get_stocked_lakes_data(days)
  total_stocked_by_hatchery_data = data_base.get_hatchery_totals(days)
  total_stocked_by_date_data = data_base.get_total_stocked_by_date_data(days)
  derby_lakes_data = data_base.get_derby_lakes_data()
  date_data_updated = data_base.get_date_data_updated()

  end_time = time()
  total_time = end_time - start_time
  print(f"It took {total_time:.2f} seconds to compute")
  assert total_time <= 4
