import datetime
from sqlalchemy.orm import Session

from . import models

def set_ticker(db: Session, ticker: models.TickerModel):
    db.add(ticker)
    db.commit()
    db.refresh(ticker)
    return ticker

def get_ticker(db: Session, ticker_id: int = None, ticker: str = None):
    if ticker_id:
        return db.query(models.TickerModel).filter(models.TickerModel.id == ticker_id).first()
    elif ticker:
        return db.query(models.TickerModel).filter(models.TickerModel.ticker == ticker).first()
    else:
        raise Exception("Must provide either ticker_id or ticker")

def get_tickers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TickerModel).offset(skip).limit(limit).all()

def get_ticker_by_name(db: Session, ticker: str):
    return db.query(models.TickerModel).filter(models.TickerModel.name == ticker).first()

def get_exchange(db: Session, exchange_id: int =None, name: str = None):
    if exchange_id:
        return db.query(models.ExchangeModel).filter(models.ExchangeModel.id == exchange_id).first()
    elif name:
        return db.query(models.ExchangeModel).filter(models.ExchangeModel.name == name).first()
    else:
        raise Exception("Must provide either exchange_id or name")

def get_exchanges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ExchangeModel).offset(skip).limit(limit).all()

def set_exchange(db: Session, exchange: models.ExchangeModel):
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange

def set_exchange_list(db: Session, exchange_list: list):
    db.add_all(exchange_list)
    db.commit()
    db.refresh(exchange_list)
    return exchange_list

def get_currency(db: Session, currency_id: int, name: str = None):
    if currency_id:
        return db.query(models.CurrencyModel).filter(models.CurrencyModel.id == currency_id).first()
    elif name:
        return db.query(models.CurrencyModel).filter(models.CurrencyModel.name == name).first()
    else:
        raise Exception("Must provide either currency_id or name")

def get_currencies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CurrencyModel).offset(skip).limit(limit).all()

def set_country(db: Session, country: models.CountryModel):
    db.add(country)
    db.commit() 
    db.refresh(country)

def get_country(db: Session, country_id: int = None, name: str = None):
    if country_id:
        return db.query(models.CountryModel).filter(models.CountryModel.id == country_id).first()
    elif name:
        return db.query(models.CountryModel).filter(models.CountryModel.name == name).first()
    else:
        raise Exception("Must provide either country_id or name")

def get_countries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CountryModel).offset(skip).limit(limit).all()

def set_city(db: Session, city: models.CityModel):
    db.add(city)
    db.commit() 
    db.refresh(city)

def get_city(db: Session, city_id: int = None, name: str = None, country_id: int = None):
    if country_id and name:
        return db.query(models.CityModel).filter(models.CityModel.country_id == country_id).filter(models.CityModel.name == name).first()
    elif city_id:
        return db.query(models.CityModel).filter(models.CityModel.id == city_id).first()
    elif name:
        return db.query(models.CityModel).filter(models.CityModel.name == name).first()
    else:
        raise Exception("Must provide either city_id or name and country_id")
 
def get_cities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CityModel).offset(skip).limit(limit).all()

def set_timezone(db: Session, timezone: models.TimezoneModel):
    db.add(timezone)
    db.commit() 
    db.refresh(timezone)

def get_timezone(db: Session, timezone_id: int = None, name: str = None):
    if timezone_id:
        return db.query(models.TimezoneModel).filter(models.TimezoneModel.id == timezone_id).first()
    elif name:
        return db.query(models.TimezoneModel).filter(models.TimezoneModel.name == name).first()
    else:
        raise Exception("Must provide either timezone_id or name")

def get_timezones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TimezoneModel).offset(skip).limit(limit).all()

def get_ticker_by_exchange(db: Session, exchange_id: int):
    return db.query(models.TickerModel).filter(models.TickerModel.exchange_id == exchange_id).all()

def set_eod_ingestor_data_store(db: Session, eod_data_store: models.EodIngestorDataStoreModel):
    db.add(eod_data_store)
    db.commit()
    db.refresh(eod_data_store)
    return eod_data_store

def get_eod_ingestor_data_store(db: Session, eod_data_store_id: int):
    return db.query(models.EodIngestorDataStoreModel).filter(models.EodIngestorDataStoreModel.id == eod_data_store_id).first()

def get_eod_ingestor_data_stores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.EodIngestorDataStoreModel).offset(skip).limit(limit).all()

def set_eod_ingestor_job_status(db: Session, eod_ingestor_job_status: models.EodIngestorJobStatusModel):
    db.add(eod_ingestor_job_status)
    db.commit()
    db.refresh(eod_ingestor_job_status)
    return eod_ingestor_job_status

def get_eod_ingestor_job_status(db: Session, eod_ingestor_job_status_id: int):
    return db.query(models.EodIngestorJobStatusModel).filter(models.EodIngestorJobStatusModel.id == eod_ingestor_job_status_id).first()

def get_eod_ingestor_job_statuses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.EodIngestorJobStatusModel).offset(skip).limit(limit).all()

def get_eod_ingestor_job_status_by_ticker(db: Session, ticker_id: int, run_date: datetime.datetime = datetime.datetime.now()):
    return db.query(models.EodIngestorJobStatusModel).filter(models.EodIngestorJobStatusModel.ticker_id == ticker_id).filter(models.EodIngestorJobStatusModel.end_date == run_date).first()

def set_eod_ingester_job_data_location(db: Session, eod_ingestor_job_data_location: models.EodIngestorJobDataLocationModel):
    db.add(eod_ingestor_job_data_location)
    db.commit()
    db.refresh(eod_ingestor_job_data_location)
    return eod_ingestor_job_data_location

def get_eod_ingestor_job_data_location(db: Session, eod_ingestor_job_data_location_id: int):
    return db.query(models.EodIngestorJobDataLocationModel).filter(models.EodIngestorJobDataLocationModel.id == eod_ingestor_job_data_location_id).first()

def set_eod_ingestor_job_data_location_list(db: Session, eod_ingestor_job_data_locations: list):
    db.add_all(eod_ingestor_job_data_locations)
    db.commit()
    db.refresh(eod_ingestor_job_data_locations)
    return eod_ingestor_job_data_locations

def get_eod_ingestor_job_data_location_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.EodIngestorJobDataLocationModel).offset(skip).limit(limit).all()

