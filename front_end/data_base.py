from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, text, desc
from front_end.data_tables import StockedLakes, DerbyLake, Utility
from datetime import datetime, timedelta
import os


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

  def get_stocked_lakes_data(self, days=365):
    start_date = self.end_date - timedelta(days=days)
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
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()
    return stocked_lakes

  def get_hatchery_totals(self, days=365):
    start_date = self.end_date - timedelta(days=days)

    hatchery_totals = self.session.query(
      StockedLakes.hatchery,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.hatchery).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(desc(text('sum_1'))).all()
    return hatchery_totals

  def get_derby_lakes_data(self):
    derby_lakes = self.conn.execute(text("SELECT * FROM derby_lakes_table")).fetchall()
    return derby_lakes

  def get_total_stocked_by_date_data(self, days=365):
    start_date = self.end_date - timedelta(days=days)

    total_stocked_by_date = self.session.query(
      StockedLakes.date,
      func.sum(StockedLakes.stocked_fish)
    ).group_by(StockedLakes.date).filter(
      StockedLakes.date.between(start_date.strftime('%b %d, %Y'), self.end_date.strftime('%b %d, %Y'))
    ).order_by(StockedLakes.date).all()
    return total_stocked_by_date

  def get_date_data_updated(self):
    last_updated = self.session.query(Utility).order_by(Utility.id.desc()).first()
    return last_updated.updated
