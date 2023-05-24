from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, text, desc
from data_tables import StockedLakes, DerbyLake, Utility
from datetime import datetime, timedelta
import os


class DataBase:
  def __init__(self):
    # Load Database
    if ("SQLALCHEMY_DATABASE_URI"):
      self.engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    else:
      self.engine = create_engine('sqlite:///sqlite.db', connect_args={"check_same_thread": False},)

    self.conn = self.engine.connect()
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

    self.end_date = datetime.now()

  def get_stocked_lakes_data(self, days=365):
      start_date = self.end_date - timedelta(days=days)
      
      query = """
      SELECT date, lake, stocked_fish, species, hatchery, weight, latitude, longitude, directions, derby_participant
      FROM stocked_lakes_table
      WHERE date BETWEEN :start_date AND :end_date
      ORDER BY date
      """
      
      stocked_lakes = self.conn.execute(text(query), start_date=start_date, end_date=self.end_date).fetchall()
      return stocked_lakes
  

  def get_hatchery_totals(self, days=365):
      start_date = self.end_date - timedelta(days=days)
      
      query = """
      SELECT hatchery, SUM(stocked_fish) AS sum_1
      FROM stocked_lakes_table
      WHERE date BETWEEN :start_date AND :end_date
      GROUP BY hatchery
      ORDER BY sum_1 DESC
      """
      
      hatchery_totals = self.conn.execute(text(query), start_date=start_date, end_date=self.end_date).fetchall()
      return hatchery_totals

  def get_derby_lakes_data(self):
    query = "SELECT * FROM derby_lakes_table"
    derby_lakes = self.conn.execute(text(query)).fetchall()
    return derby_lakes

  def get_total_stocked_by_date_data(self, days=365):
    start_date = self.end_date - timedelta(days=days)
    
    query = """
    SELECT date, SUM(stocked_fish) AS sum_1
    FROM stocked_lakes_table
    WHERE date BETWEEN :start_date AND :end_date
    GROUP BY date
    ORDER BY date
    """
    
    total_stocked_by_date = self.conn.execute(text(query), start_date=start_date, end_date=self.end_date).fetchall()
    
    # 
    if str(self.engine) == "Engine(sqlite:///sqlite.db)":
      total_stocked_by_date = [(datetime.strptime(date_str, "%Y-%m-%d"), stocked_fish) for date_str, stocked_fish in total_stocked_by_date]
    
    return total_stocked_by_date

  def get_date_data_updated(self):
    query = "SELECT updated FROM utility_table ORDER BY id DESC LIMIT 1"
    last_updated = self.conn.execute(text(query)).scalar()
    return last_updated
