from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, text, desc
from datetime import datetime, timedelta
import os

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, func

# Create a SQLAlchemy base
Base = declarative_base()


# Create the stocked_lakes_table class
class StockedLakes(Base):
  __tablename__ = 'stocked_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)
  stocked_fish = Column(Integer)
  species = Column(String)
  weight = Column(Float)
  hatchery = Column(String)
  date = Column(Date)
  latitude = Column(Float)
  longitude = Column(Float)
  directions = Column(String)
  derby_participant = Column(Boolean)


# Create the derby_lakes_table class
class DerbyLake(Base):
  __tablename__ = 'derby_lakes_table'
  id = Column(Integer, primary_key=True)
  lake = Column(String)


# Create the derby_lakes_table class
class Utility(Base):
  __tablename__ = 'utility_table'
  id = Column(Integer, primary_key=True)
  updated = Column(Date)


class DataBase:
  def __init__(self):
    # Load Database
    if os.getenv("SQLALCHEMY_DATABASE_URI"):
      self.engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"))
    else:
      print("USING SQLITE DB")
      self.engine = create_engine('sqlite:///front_end/sqlite.db', connect_args={"check_same_thread": False},)

    self.conn = self.engine.connect()
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

    self.end_date = datetime.now()
    self.insert_counter = 0


  def get_stocked_lakes_data(self, days=365):
      start_date = self.end_date - timedelta(days=days)
      
      query = """
      SELECT date, lake, stocked_fish, species, hatchery, weight, latitude, longitude, directions, derby_participant
      FROM stocked_lakes_table
      WHERE date BETWEEN :start_date AND :end_date
      ORDER BY date
      """
      
      # stocked_lakes = self.conn.execute(text(query), parameters=dict(start_date=start_date, end_date=self.end_date)).fetchall()

    # Query the StockedLake model
      stocked_lakes = self.session.query(StockedLakes) \
        .filter(StockedLakes.date.between(start_date, self.end_date)) \
        .order_by(StockedLakes.date) \
        .all()

      # self.session.close()
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
      
      hatchery_totals = self.conn.execute(text(query),  parameters=dict(start_date=start_date, end_date=self.end_date)).fetchall()
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
    
    total_stocked_by_date = self.conn.execute(text(query),  parameters=dict(start_date=start_date, end_date=self.end_date)).fetchall()
    
    # 
    if str(self.engine) == "Engine(sqlite:///front_end/sqlite.db)":
      total_stocked_by_date = [(datetime.strptime(date_str, "%Y-%m-%d"), stocked_fish) for date_str, stocked_fish in total_stocked_by_date]
    
    return total_stocked_by_date

  def get_date_data_updated(self):
    query = "SELECT updated FROM utility_table ORDER BY id DESC LIMIT 1"
    last_updated = self.conn.execute(text(query)).scalar()
    return last_updated
  
  def write_data(self, scraper):
    if str(self.engine) == "Engine(sqlite:///front_end/sqlite.db)":
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        
    self.write_derby_data(scraper)
    self.write_lake_data(scraper)
    self.write_utility_data()
    self.session.commit()
    self.session.close()

  def write_derby_data(self, scraper):
    derby_lakes = scraper.derby_lake_names
    for lake in derby_lakes:
      for item in scraper.df:
        if lake.capitalize() in item['lake'].capitalize():
          item['derby_participant'] = True
          existing_lake = self.session.query(DerbyLake).filter_by(lake=lake).first()
          if existing_lake:
            continue  # skip if the lake already exists in the table
          self.session.add(DerbyLake(lake=lake))

  def write_lake_data(self, scraper):
    for lake_data in scraper.df:
      # check if entry already exists in the table
      existing_lake = self.session.query(StockedLakes).filter_by(lake=lake_data['lake'],
                                                                 stocked_fish=lake_data['stocked_fish'],
                                                                 date=lake_data['date']).first()
      if existing_lake:
        continue  # skip if the lake already exists in the table

      # add the lake to the table if it doesn't exist
      lake = StockedLakes(lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date'],
                          latitude=lake_data['latitude'], longitude=lake_data['longitude'],
                          directions=lake_data['directions'], derby_participant=lake_data['derby_participant'],
                          weight=lake_data['weight'], species=lake_data['species'], hatchery=lake_data['hatchery'])

      self.session.add(lake)

      self.insert_counter += 1

    print(f'There were {self.insert_counter} entries added to {str(StockedLakes.__tablename__)}')

  def write_utility_data(self):
    self.session.add(Utility(updated=datetime.now().date()))

  def back_up_database(self):
    all_stocked_lakes = self.session.query(StockedLakes).all()

    backup_file_txt = 'back_end/backup_data.txt'
    backup_file_sql = 'back_end/backup_data.sql'

    if os.path.exists(backup_file_txt):
      os.remove(backup_file_txt)
    if os.path.exists(backup_file_sql):
      os.remove(backup_file_sql)

    with open(backup_file_txt, 'w') as f:
      for row in all_stocked_lakes:
        # Write each column value separated by a comma
        f.write(
          f"{row.id},{row.lake},{row.stocked_fish},{row.species},{row.weight},{row.hatchery},{row.date},{row.latitude},{row.longitude},{row.directions},{row.derby_participant}\n")

    with open(backup_file_sql, 'w') as f:
      for row in all_stocked_lakes:
        # Write an INSERT INTO statement for each row
        f.write(
          f"INSERT INTO stocked_lakes_table (id, lake, stocked_fish, species, weight, hatchery, date, latitude, longitude, directions, derby_participant) VALUES ({row.id}, '{row.lake}', {row.stocked_fish}, '{row.species}', {row.weight}, '{row.hatchery}', '{row.date}', '{row.latitude}', '{row.longitude}', '{row.directions}', {row.derby_participant});\n")

    print(f"Database backed up to {backup_file_txt} and {backup_file_sql}")
