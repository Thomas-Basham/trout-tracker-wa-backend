# database.py
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, joinedload
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Float, TIMESTAMP, exists, ForeignKey, text  # text???
from datetime import datetime, timedelta
import os

# Create a SQLAlchemy base
Base = declarative_base()


class WaterLocations(Base):
    __tablename__ = 'water_locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_html_name = Column(String, unique=True)  # what wdfw named
    water_name_cleaned = Column(String)  # the cleaned name after scraping
    latitude = Column(Float)
    longitude = Column(Float)
    directions = Column(String)
    created_at = Column(TIMESTAMP)
    derby_participant = Column(Boolean)
# Create the stocked_lakes_table class


class StockedLakes(Base):
    __tablename__ = 'stocked_lakes_table'
    id = Column(Integer, primary_key=True)
    lake = Column(String)  # plans to move to FK
    stocked_fish = Column(Integer)
    species = Column(String)
    weight = Column(Float)
    hatchery = Column(String)
    date = Column(Date)
    latitude = Column(Float)  # plans to move to FK
    longitude = Column(Float)  # plans to move to FK
    directions = Column(String)  # plans to move to FK
    derby_participant = Column(Boolean)  # plans to move to FK
    # Replace raw lat/lng/directions with FK
    water_location_id = Column(Integer, ForeignKey('water_locations.id'))
    water_location = relationship("WaterLocations")

    def to_dict(self):
        return {
            "date": self.date,
            "lake": self.lake,
            "stocked_fish": self.stocked_fish,
            "species": self.species,
            "hatchery": self.hatchery,
            "weight": self.weight,
            "derby_participant": self.derby_participant,
            "latitude": self.water_location.latitude if self.water_location else None,
            "longitude": self.water_location.longitude if self.water_location else None,
            "directions": self.water_location.directions if self.water_location else None,
            "water_location_id": self.water_location_id,
            "water_location": self.water_location
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

        if db_user and db_password and db_name and db_host:
            database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={"connect_timeout": 20}
            )
        else:
            print("USING SQLITE DB")
            self.engine = create_engine(
                'sqlite:///api/sqlite.db', connect_args={"check_same_thread": False},)

        self.conn = self.engine.connect()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.insert_counter = 0

    def get_stocked_lakes_data(
        self,
        end_date: datetime = datetime.now(),
        start_date: datetime = datetime.now() - timedelta(days=7)
    ):
        """
        Return all stocked lake records between start_date and end_date,
        but join from water_locations so we can pull the cleaned name and
        location info first.
        """
        # Query WaterLocations → join → StockedLakes
        rows = (
            self.session
                .query(WaterLocations, StockedLakes)
                .join(
                    StockedLakes,
                    StockedLakes.water_location_id == WaterLocations.id
                )
            .filter(StockedLakes.date.between(start_date, end_date))
            .order_by(StockedLakes.date.desc())
            .all()
        )

        # Flatten into identical dicts your front-end expects
        result = []
        for water_loc, stocked in rows:
            rec = {
                "date": stocked.date.isoformat() if stocked.date else None,
                "lake": water_loc.water_name_cleaned,
                "stocked_fish": stocked.stocked_fish,
                "species": stocked.species,
                "hatchery": stocked.hatchery,
                "weight": stocked.weight,
                "derby_participant": water_loc.derby_participant,
                "water_location_id": water_loc.id,
                "latitude": water_loc.latitude,
                "longitude": water_loc.longitude,
                "directions": water_loc.directions,
            }
            result.append(rec)

        return result

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

    def get_water_location(self, original_html_name):
        water_location = self.session.query(WaterLocations).filter(
            WaterLocations.original_html_name.ilike(
                original_html_name)
        ).first()
        return water_location

    def write_data(self, data):
        if str(self.engine) == "Engine(sqlite:///api/sqlite.db)":
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)

        # self.write_derby_data(data)
        self.write_lake_data(data)
        self.write_utility_data()
        self.session.commit()
        self.session.close()

    def write_derby_data(self, data):
        derby_lakes = data.derby_lake_names
        if derby_lakes:
            for lake in derby_lakes:
                for item in data:
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

    def insert_water_location(self, original_html_name, water_name_cleaned, latitude, longitude, directions, derby_participant):
        """Insert a new water location unless it already exists by original_html_name."""
        # existing_location = self.session.query(WaterLocations).filter_by(
        #     original_html_name=original_html_name).first()
        if self.record_exists(WaterLocations, original_html_name=original_html_name):
            print(
                f"Skipping insert — Water location '{original_html_name}' already exists.")
            return
        new_location = WaterLocations(
            original_html_name=original_html_name,
            water_name_cleaned=water_name_cleaned,
            latitude=latitude,
            longitude=longitude,
            directions=directions,
            derby_participant=derby_participant,
            created_at=datetime.now()
        )
        self.session.add(new_location)
        self.session.commit()
        print(f"✅ Inserted new water location: {original_html_name}")

    def write_lake_data(self, data):
        for lake_data in data:
            # Try to find matching water location
            water_location = self.get_water_location(
                lake_data['original_html_name'])

            if not water_location:
                # Insert new water location if missing
                water_location = WaterLocations(
                    original_html_name=lake_data['original_html_name'],
                    water_name_cleaned=lake_data['lake'],
                    latitude=lake_data['latitude'],
                    longitude=lake_data['longitude'],
                    directions=lake_data['directions'],
                    created_at=datetime.now(),
                    derby_participant=lake_data.get('derby_participant', False)
                )
                self.session.add(water_location)
                self.session.flush()  # assign new id
                print(
                    f"✅ Added new water location '{lake_data['lake']}' with id {water_location.id}")
            # Create stocked lake with FK reference
            lake = StockedLakes(
                lake=lake_data['lake'],
                stocked_fish=lake_data['stocked_fish'],
                date=lake_data['date'],
                derby_participant=lake_data['derby_participant'],
                weight=lake_data['weight'],
                species=lake_data['species'],
                hatchery=lake_data['hatchery'],
                water_location_id=water_location.id
            )

            # check if entry already exists in the table
            if self.record_exists(StockedLakes, lake=lake_data['lake'], stocked_fish=lake_data['stocked_fish'], date=lake_data['date']):
                print(
                    f'Skipped in db. already added {lake_data["lake"]} {lake_data["stocked_fish"]} {lake_data["date"]}')
                continue  # Skip if exists

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

    # def backfill_water_location_fields(self):
        print("🔄 Backfilling latitude, longitude, and directions from stocked_lakes into water_locations...")
        updated_count = 0

        # Fetch all water locations
        water_locations = self.session.query(WaterLocations).filter_by(
            latitude=0).all()

        for wl in water_locations:
            # Try to find a stocked lake with matching cleaned name
            stocked = self.session.query(StockedLakes).filter_by(
                lake=wl.water_name_cleaned).first()
            if stocked and (stocked.latitude or stocked.longitude or stocked.directions):
                # Update fields if not already set
                changed = False
                if wl.latitude != stocked.latitude:
                    wl.latitude = stocked.latitude
                    changed = True
                if wl.longitude != stocked.longitude:
                    wl.longitude = stocked.longitude
                    changed = True
                if wl.directions != stocked.directions:
                    wl.directions = stocked.directions
                    changed = True

                if changed:
                    updated_count += 1
                    print(
                        f"✅ Updated {wl.water_name_cleaned} with lat/lon/directions")

        self.session.commit()
        print(f"Done. Updated {updated_count} water location entries.")

    # def backfill_water_location_ids(self):
        print("Backfilling water_location_id in stocked_lakes...")
        updated_count = 0

        stocked_lakes = self.session.query(StockedLakes).filter_by(
            water_location_id=None).all()

        for sl in stocked_lakes:
            if sl.water_location_id:
                continue  # already linked

            match = self.session.query(WaterLocations).filter_by(
                water_name_cleaned=sl.lake).first()
            if match:
                sl.water_location_id = match.id
                updated_count += 1
                print(
                    f"✅ Linked lake '{sl.lake}' to water_location_id {match.id}")
            else:
                print(f"❌ No match found for lake '{sl.lake}'")

        self.session.commit()
        self.session.close()

        print(f"🎉 Done. Backfilled {updated_count} stocked lake entries.")
