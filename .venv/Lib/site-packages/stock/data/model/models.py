from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base


class ExchangeModel(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True )
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    acronym = Column(String, unique=False, index=True)
    mic = Column(String, unique=False, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), index=True)
    timezone_id = Column(Integer, ForeignKey("timezones.id"), index=True)
    
    tickers = relationship("TickerModel", cascade="all,delete", back_populates="exchange")
    country = relationship("CountryModel", back_populates="exchanges")
    city = relationship("CityModel", back_populates="exchanges")
    timezone = relationship("TimezoneModel", back_populates="exchanges")

class TimezoneModel(Base):
    __tablename__ = "timezones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    abbr = Column(String, index=True)
    dst = Column(String, index=True)

    exchanges = relationship("ExchangeModel", cascade="all,delete", back_populates="timezone")
    job_statuses = relationship("EodIngestorJobStatusModel", cascade="all,delete", back_populates="timezone")


class CountryModel(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    code = Column(String, index=True)

    exchanges = relationship("ExchangeModel", cascade="all,delete", back_populates="country")
    cities = relationship("CityModel", cascade="all,delete", back_populates="country")


class CityModel(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    country_id = Column(Integer, ForeignKey("countries.id"), index=True)

    country = relationship("CountryModel", back_populates="cities")
    exchanges = relationship("ExchangeModel", cascade="all,delete", back_populates="city")

class TickerModel(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), index=True)
    ticker = Column(String, index=True)

    exchange = relationship("ExchangeModel", back_populates="tickers")
    job_statuses = relationship("EodIngestorJobStatusModel", cascade="all,delete", back_populates="ticker")


class CurrencyModel(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    code = Column(String, index=True)

class EodIngestorDataStoreModel(Base):
    __tablename__ = "eod_ingestor_data_stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    url = Column(String, index=True)
    subscription_id = Column(String, index=True)
    container = Column(String, index=True)
    tenant_id = Column(String, index=True, nullable=True)

    job_statuses = relationship("EodIngestorJobStatusModel", cascade="all,delete", back_populates="data_store")
    data_locations = relationship("EodIngestorJobDataLocationModel", cascade="all,delete", back_populates="data_store")

class EodIngestorJobStatusModel(Base):
    __tablename__ = "eod_ingestor_job_status"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    status = Column(String, index=False)
    message = Column(String, index=False, nullable=True)
    data_store_id = Column(Integer, ForeignKey("eod_ingestor_data_stores.id"), index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), index=True)
    timezone_id = Column(Integer, ForeignKey("timezones.id"), index=True)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)

    data_store = relationship("EodIngestorDataStoreModel", back_populates="job_statuses")
    ticker = relationship("TickerModel", back_populates="job_statuses")
    timezone = relationship("TimezoneModel", back_populates="job_statuses")
    data_locations = relationship("EodIngestorJobDataLocationModel", cascade="all,delete", back_populates="job_status")

class EodIngestorJobDataLocationModel(Base):
    __tablename__ = "eod_ingestor_job_data_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_generated = Column(
        DateTime, server_default=func.current_timestamp(), index=False
    )
    job_status_id = Column(
        Integer, ForeignKey("eod_ingestor_job_status.id"), index=True
    )
    data_store_id = Column(Integer, ForeignKey("eod_ingestor_data_stores.id"), index=True)
    blob = Column(String, index=True)

    job_status = relationship("EodIngestorJobStatusModel", back_populates="data_locations")
    data_store = relationship("EodIngestorDataStoreModel", back_populates="data_locations")