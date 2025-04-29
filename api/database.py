# database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, text, desc
from datetime import datetime, timedelta
import os

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, func
from sqlalchemy import exists

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

    def to_dict(self):
        return {
            "date": self.date,
            "lake": self.lake,
            "stocked_fish": self.stocked_fish,
            "species": self.species,
            "hatchery": self.hatchery,
            "weight": self.weight,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "directions": self.directions,
            "derby_participant": self.derby_participant
        }


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
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_name = os.getenv("POSTGRES_DB")
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_PORT", "5432")  # Default Postgres port

        if os.getenv("SQLALCHEMY_DATABASE_URI"):
            self.engine = create_engine(
                os.getenv("SQLALCHEMY_DATABASE_URI"),
                pool_pre_ping=True,
                pool_recycle=1800,  # Recycle connections after 30 minutes
                # Set a connection timeout of 10 seconds)
                connect_args={"connect_timeout": 10}
            )
        # if db_user and db_password and db_name and db_host:
        #     database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

        #     self.engine = create_engine(
        #         database_url,
        #         pool_pre_ping=True,
        #         pool_recycle=1800,
        #         connect_args={"connect_timeout": 10}
        #     )
        else:
            print("USING SQLITE DB")
            self.engine = create_engine(
                'sqlite:///api/sqlite.db', connect_args={"check_same_thread": False},)

        self.conn = self.engine.connect()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.insert_counter = 0

    def get_stocked_lakes_data(self, end_date=datetime.now(), start_date=datetime.now() - timedelta(days=7)):

        # Query the StockedLake model
        stocked_lakes = self.session.query(StockedLakes) \
            .filter(StockedLakes.date.between(start_date, end_date)) \
            .order_by(StockedLakes.date.desc()) \
            .all()

        # self.session.close()
        return stocked_lakes

    def get_hatchery_totals(self, end_date=datetime.now(), start_date=datetime.now() - timedelta(days=7)):

        query = """
      SELECT hatchery, SUM(stocked_fish) AS sum_1
      FROM stocked_lakes_table
      WHERE date BETWEEN :start_date AND :end_date
      GROUP BY hatchery
      ORDER BY sum_1 DESC
      """

        hatchery_totals = self.conn.execute(
            text(query),  start_date=start_date, end_date=end_date).fetchall()
        print("hatchery_totals", hatchery_totals)
        return hatchery_totals

    def get_total_stocked_by_date_data(self,  end_date=datetime.now(), start_date=datetime.now() - timedelta(days=7)):

        query = """
        SELECT date, SUM(stocked_fish) AS sum_1
        FROM stocked_lakes_table
        WHERE date BETWEEN :start_date AND :end_date
        GROUP BY date
        ORDER BY date
        """

        total_stocked_by_date = self.conn.execute(
            text(query),  start_date=start_date, end_date=end_date).fetchall()

        if str(self.engine) == "Engine(sqlite:///api/sqlite.db)":
            total_stocked_by_date = [(datetime.strptime(date_str, "%Y-%m-%d"), stocked_fish)
                                     for date_str, stocked_fish in total_stocked_by_date]

        return total_stocked_by_date

    def get_derby_lakes_data(self):
        query = "SELECT * FROM derby_lakes_table"
        derby_lakes = self.conn.execute(text(query)).fetchall()
        return derby_lakes

    def get_unique_hatcheries(self):
        query = "SELECT DISTINCT hatchery FROM stocked_lakes_table ORDER BY hatchery"
        unique_hatcheries = self.conn.execute(text(query)).fetchall()
        print(unique_hatcheries)
        return [row[0] for row in unique_hatcheries]

    def get_date_data_updated(self):
        query = "SELECT updated FROM utility_table ORDER BY id DESC LIMIT 1"
        last_updated = self.conn.execute(text(query)).scalar()
        return last_updated

    def write_data(self, scraper):
        if str(self.engine) == "Engine(sqlite:///api/sqlite.db)":
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)

        self.write_derby_data(scraper)
        self.write_lake_data(scraper)
        self.write_utility_data()
        self.session.commit()
        self.session.close()

    def write_derby_data(self, scraper):
        derby_lakes = scraper.derby_lake_names
        if derby_lakes:
            for lake in derby_lakes:
                for item in scraper.df:
                    if lake.capitalize() in item['lake'].capitalize():
                        item['derby_participant'] = True
                        existing_lake = self.session.query(
                            DerbyLake).filter_by(lake=lake).first()
                        if existing_lake:
                            continue  # skip if the lake already exists in the table
                        self.session.add(DerbyLake(lake=lake))
        else:
            # If there are no derby lakes, clear all derby participants from Stocked Lake table, delete all derby table entries
            self.session.query(DerbyLake).delete()

            lakes_to_update = self.session.query(
                StockedLakes).filter_by(derby_participant=True)
            for lake in lakes_to_update:
                lake.derby_participant = False

    def record_exists(self, model, **kwargs):
        """Efficiently check if a record exists in the database."""
        return self.session.query(exists().where(
            *(getattr(model, key) == value for key, value in kwargs.items())
        )).scalar()

    # TODO: This feel super eneficient. Optimize!
    def write_lake_data(self, scraper):
        for lake_data in scraper.df:
            # check if entry already exists in the table
            # existing_lake = self.session.query(StockedLakes).filter_by(lake=lake_data['lake'],
            #                                                            stocked_fish=lake_data['stocked_fish'],
            #                                                            date=lake_data['date']).first()
            # if existing_lake:
            #     continue  # skip if the lake already exists in the table
            if self.record_exists(StockedLakes, lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date']):
                print(
                    f'Skipped in db. already added {lake_data["lake"]} {lake_data["stocked_fish"]} {lake_data["date"]}')
                continue  # Skip if exists
            
            # add the lake to the table if it doesn't exist
            lake = StockedLakes(lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date'],
                                latitude=lake_data['latitude'], longitude=lake_data['longitude'],
                                directions=lake_data['directions'], derby_participant=lake_data['derby_participant'],
                                weight=lake_data['weight'], species=lake_data['species'], hatchery=lake_data['hatchery'])

            self.session.add(lake)

            self.insert_counter += 1

        print(
            f'There were {self.insert_counter} entries added to {str(StockedLakes.__tablename__)}')

    def write_utility_data(self):
        self.session.add(Utility(updated=datetime.now().date()))

    def back_up_database(self):
        all_stocked_lakes = self.session.query(StockedLakes).all()

        backup_file_txt = 'backup_data.txt'
        backup_file_sql = 'backup_data.sql'

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
