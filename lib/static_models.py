from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Agency(Base):
    __tablename__ = "agency"

    agency_id = Column(String(64), primary_key=True)
    agency_name = Column(Text, nullable=False)
    agency_url = Column(Text, nullable=False)
    agency_timezone = Column(String(32), nullable=False)
    agency_lang = Column(String(32), nullable=False)
    agency_phone = Column(String(32))
    agency_fare_url = Column(Text)
    agency_email = Column(Text)

    # リレーションシップ
    agency_jp = relationship("AgencyJp", back_populates="agency", uselist=False)
    routes = relationship("Routes", back_populates="agency")
    fare_attributes = relationship("FareAttributes", back_populates="agency")


class AgencyJp(Base):
    __tablename__ = "agency_jp"

    agency_id = Column(String(64), ForeignKey("agency.agency_id"), primary_key=True)
    agency_official_name = Column(Text)
    agency_zip_number = Column(String(32))
    agency_address = Column(Text)
    agency_president_pos = Column(Text)
    agency_president_name = Column(Text)

    # リレーションシップ
    agency = relationship("Agency", back_populates="agency_jp")


class Routes(Base):
    __tablename__ = "routes"

    route_id = Column(String(64), primary_key=True)
    agency_id = Column(String(64), ForeignKey("agency.agency_id"), nullable=False)
    route_short_name = Column(String(64))
    route_long_name = Column(Text)
    route_desc = Column(Text)
    route_type = Column(String(32), nullable=False)
    route_url = Column(Text)
    route_color = Column(String(8))
    route_text_color = Column(String(8))
    jp_parent_route_id = Column(String(64))

    # リレーションシップ
    agency = relationship("Agency", back_populates="routes")
    routes_jp = relationship("RoutesJp", back_populates="routes")
    trips = relationship("Trips", back_populates="routes")
    fare_rules = relationship("FareRules", back_populates="routes")


class RoutesJp(Base):
    __tablename__ = "routes_jp"

    route_id = Column(String(64), ForeignKey("routes.route_id"), primary_key=True)
    route_update_date = Column(String(32))
    origin_stop = Column(Text)
    via_stop = Column(Text)
    destination_stop = Column(Text)
    jp_parent_route_id = Column(Text)

    # リレーションシップ
    routes = relationship("Routes", back_populates="routes_jp")


class Calendar(Base):
    __tablename__ = "calendar"

    service_id = Column(String(64), primary_key=True)
    monday = Column(String(2))
    tuesday = Column(String(2))
    wednesday = Column(String(2))
    thursday = Column(String(2))
    friday = Column(String(2))
    saturday = Column(String(2))
    sunday = Column(String(2))
    start_date = Column(String(16))
    end_date = Column(String(16))

    # リレーションシップ
    trips = relationship("Trips", back_populates="calendar")


class CalendarDates(Base):
    __tablename__ = "calendar_dates"

    service_id = Column(String(64), primary_key=True)
    date = Column(String(16), primary_key=True)
    exception_type = Column(String(2))


class OfficeJp(Base):
    __tablename__ = "office_jp"

    office_id = Column(String(64), primary_key=True)
    office_name = Column(Text)
    office_url = Column(Text)
    office_phone = Column(String(32))

    # リレーションシップ
    trips = relationship("Trips", back_populates="office_jp")


class Shapes(Base):
    __tablename__ = "shapes"

    shape_id = Column(String(64), primary_key=True)
    shape_pt_lat = Column(String(16))
    shape_pt_lon = Column(String(16))
    shape_pt_sequence = Column(Integer)
    shape_dist_traveled = Column(Integer)

    # リレーションシップ
    trips = relationship("Trips", back_populates="shapes")


class Trips(Base):
    __tablename__ = "trips"

    trip_id = Column(String(64), primary_key=True)
    route_id = Column(String(64), ForeignKey("routes.route_id"))
    service_id = Column(String(64), ForeignKey("calendar.service_id"))
    trip_headsign = Column(Text)
    trip_short_name = Column(Text)
    direction_id = Column(String(2))
    block_id = Column(Text)
    shape_id = Column(String(64), ForeignKey("shapes.shape_id"))
    wheelchair_accessible = Column(String(2))
    bikes_allowed = Column(String(2))
    jp_trip_desc = Column(Text)
    jp_trip_desc_symbol = Column(Text)
    jp_office_id = Column(String(64), ForeignKey("office_jp.office_id"))

    # リレーションシップ
    routes = relationship("Routes", back_populates="trips")
    calendar = relationship("Calendar", back_populates="trips")
    office_jp = relationship("OfficeJp", back_populates="trips")
    shapes = relationship("Shapes", back_populates="trips")
    frequencies = relationship("Frequencies", back_populates="trips")
    stop_times = relationship("StopTimes", back_populates="trips")


class Frequencies(Base):
    __tablename__ = "frequencies"

    trip_id = Column(String(64), ForeignKey("trips.trip_id"), primary_key=True)
    start_time = Column(String(12), primary_key=True)
    end_time = Column(String(12))
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    # リレーションシップ
    trips = relationship("Trips", back_populates="frequencies")


class Stops(Base):
    __tablename__ = "stops"

    stop_id = Column(String(64), primary_key=True)
    stop_code = Column(String(64))
    stop_name = Column(Text)
    stop_desc = Column(Text)
    stop_lat = Column(String(16))
    stop_lon = Column(String(16))
    zone_id = Column(String(64))
    stop_url = Column(Text)
    location_type = Column(String(2))
    parent_station = Column(String(64))
    stop_timezone = Column(String(32))
    wheelchair_boarding = Column(String(2))
    platform_code = Column(Text)

    # リレーションシップ
    stop_times = relationship("StopTimes", back_populates="stops")


class StopTimes(Base):
    __tablename__ = "stop_times"

    trip_id = Column(String(64), ForeignKey("trips.trip_id"), primary_key=True)
    stop_id = Column(String(64), ForeignKey("stops.stop_id"), primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)
    arrival_time = Column(String(12))
    departure_time = Column(String(12))
    stop_headsign = Column(Text)
    pickup_type = Column(String(2))
    drop_off_type = Column(String(2))
    shape_dist_traveled = Column(Integer)
    timepoint = Column(Integer)

    # リレーションシップ
    trips = relationship("Trips", back_populates="stop_times")
    stops = relationship("Stops", back_populates="stop_times")


class Transfers(Base):
    __tablename__ = "transfers"

    from_stop_id = Column(String(64), primary_key=True)
    to_stop_id = Column(String(64), primary_key=True)
    transfer_type = Column(String(2))
    min_transfer_type = Column(Integer)


class FareAttributes(Base):
    __tablename__ = "fare_attributes"

    fare_id = Column(String(64), primary_key=True)
    price = Column(Integer)
    currency_type = Column(String(16))
    payment_method = Column(String(2))
    transfers = Column(String(2))
    transfer_duration = Column(Integer)
    agency_id = Column(String(64), ForeignKey("agency.agency_id"))

    # リレーションシップ
    agency = relationship("Agency", back_populates="fare_attributes")
    fare_rules = relationship("FareRules", back_populates="fare_attributes")


class FareRules(Base):
    __tablename__ = "fare_rules"

    fare_id = Column(
        String(64),
        ForeignKey("fare_attributes.fare_id"),
        primary_key=True,
    )
    route_id = Column(String(64), ForeignKey("routes.route_id"), primary_key=True)
    origin_id = Column(String(64))
    destination_id = Column(String(64))
    contains_id = Column(String(64))

    # リレーションシップ
    fare_attributes = relationship("FareAttributes", back_populates="fare_rules")
    routes = relationship("Routes", back_populates="fare_rules")


class FeedInfo(Base):
    __tablename__ = "feed_info"

    feed_publisher_name = Column(Text, nullable=False, primary_key=True)
    feed_publisher_url = Column(Text, nullable=False)
    feed_lang = Column(String(16), nullable=False)
    feed_start_date = Column(String(12))
    feed_end_date = Column(String(12))
    feed_version = Column(Text)


class Translations(Base):
    __tablename__ = "translations"

    trans_id = Column(Text, nullable=False, primary_key=True)
    lang = Column(String(8), nullable=False, primary_key=True)
    translation = Column(Text, nullable=False)
