import requests
import logging
import os
from stock.data.model.database import SessionLocal
from stock.data.model.crud import (
    get_city,
    get_country,
    get_exchange,
    get_timezone,
)
from stock.data.model.models import (
    CityModel,
    CountryModel,
    CurrencyModel,
    EodIngestorDataStoreModel,
    ExchangeModel,
    TickerModel,
    TimezoneModel,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_PARAMS = {"access_key": os.getenv("MARKETSTACK_API_KEY"), "limit": 1000}
MAX_PAGES = 100
MARKETSTACK_API = "http://api.marketstack.com/v1"


def get_requests_with_offset(endpoint, initial_offset):
    offset = initial_offset
    data = []
    while True:
        _data = requests.get(
            f"{MARKETSTACK_API}/{endpoint}", params={**DEFAULT_PARAMS, "offset": offset}
        ).json()
        data.extend(_data["data"])
        if (
            DEFAULT_PARAMS["limit"] > _data["pagination"]["count"]
            or offset >= MAX_PAGES
        ):
            break
        offset += 1

    return {"data": remove_dupes(data)}


def remove_dupes(data):
    new_d = []
    for x in data:
        if x not in new_d:
            new_d.append(x)
    return new_d


def get_ext_timezones_list():
    """Get list of timezones from Marketstack API"""
    logger.info("Getting list of timezones from Marketstack API")
    return get_requests_with_offset("timezones", 0)


def get_ext_currencies_list():
    """Get list of currencies from Marketstack API"""
    logger.info("Getting list of currencies from Marketstack API")
    return get_requests_with_offset("currencies", 0)


def get_ext_exchanges_list():
    """Get list of exchanges from Marketstack API"""
    logger.info("Getting list of exchanges from Marketstack API")
    _exchanges = get_requests_with_offset("exchanges", 0)
    exchanges = []
    for exchange in _exchanges["data"]:
        if exchange["name"] != "INDEX":
            exchanges.append(exchange)
    return {"data": exchanges}


def get_ext_countries_list():
    """Get list of countries from Marketstack API"""
    logger.info("Getting list of countries from Marketstack API")
    exchanges = get_ext_exchanges_list()
    countries = []
    for exchange in exchanges["data"]:
        if exchange["country"] is not None:
            countries.append(
                {"name": exchange["country"], "code": exchange["country_code"]}
            )

    return {"data": countries}


def get_ext_cities_list():
    """Get list of cities from Marketstack API"""
    logger.info("Getting list of cities from Marketstack API")
    exchanges = get_ext_exchanges_list()
    cities = []
    for exchange in exchanges["data"]:
        if exchange["city"] is not None:
            cities.append({"name": exchange["city"], "country": exchange["country"]})

    return {"data": cities}


def get_ext_tickers_list():
    """Get list of tickers from Marketstack API"""
    logger.info("Getting list of tickers from Marketstack API")
    tickers = get_requests_with_offset("tickers", 0)
    return {"data": tickers["data"]}


def get_ext_eod_exchange(exchange, date=None):
    """Get EOD data for an exchange from Marketstack API"""
    logger.info("Get EOD data for an exchange from Marketstack API")
    if date is not None:
        tickers = get_requests_with_offset(f"exchange/{exchange.mic}/eod/{date}", 0)
    else:
        tickers = get_requests_with_offset(f"exchange/{exchange.mic}/eod/latest", 0)
    return {"data": tickers["data"]}


def seed_tickers():
    """Seed tickers in database"""
    logger.info("Seeding tickers in database")
    db = SessionLocal()
    tickers = get_ext_tickers_list()
    for ticker in tickers["data"]:
        try:
            db_ticker = TickerModel(
                name=ticker["name"],
                ticker=ticker["symbol"],
                exchange_id=get_exchange(db, name=ticker["stock_exchange"]["name"]).id,
            )
            db.add(db_ticker)
        except Exception as e:
            logger.warning(f'Error seeding ticker {ticker["symbol"]}: {e}')
    db.commit()


def seed_cities():
    """Seed cities in database"""
    logger.info("Seeding cities in database")
    db = SessionLocal()
    cities = get_ext_cities_list()
    for city in cities["data"]:
        db_city = CityModel(
            name=city["name"], country_id=get_country(db, name=city["country"]).id
        )
        db.add(db_city)
    db.commit()


def seed_countries():
    """Seed countries in database"""
    logger.info("Seeding countries in database")
    db = SessionLocal()
    countries = get_ext_countries_list()
    for country in countries["data"]:
        db_country = CountryModel(name=country["name"], code=country["code"])
        db.add(db_country)
    db.commit()


def seed_exchanges():
    """Seed exchanges in database"""
    logger.info("Seeding exchanges in database")
    db = SessionLocal()
    exchanges = get_ext_exchanges_list()
    for exchange in exchanges["data"]:
        try:
            db_exchange = ExchangeModel(
                name=exchange["name"],
                acronym=exchange["acronym"],
                mic=exchange["mic"],
                country_id=get_country(db, name=exchange["country"]).id,
                city_id=get_city(
                    db,
                    name=exchange["city"],
                    country_id=get_country(db, name=exchange["country"]).id,
                ).id,
                timezone_id=get_timezone(db, name=exchange["timezone"]["timezone"]).id,
            )
            db.add(db_exchange)
        except Exception as e:
            logger.warning(f'Error seeding exchange {exchange["name"]}: {e}')
    db.commit()


def seed_currencies():
    """Seed currencies in database"""
    logger.info("Seeding currencies in database")
    db = SessionLocal()
    currencies = get_ext_currencies_list()
    for currency in currencies["data"]:
        db_currency = CurrencyModel(name=currency["name"], code=currency["code"])
        db.add(db_currency)
    db.commit()


def seed_timezones():
    """Seed timezones in database"""
    logger.info("Seeding timezones in database")
    db = SessionLocal()
    timezones = get_ext_timezones_list()
    for timezone in timezones["data"]:
        db_timezone = TimezoneModel(
            name=timezone["timezone"], abbr=timezone["abbr"], dst=timezone["abbr_dst"]
        )
        db.add(db_timezone)
    db.commit()


def seed_eod_ingestor_datastore():
    """Seed EOD Ingestor Datastore"""
    logger.info("Seeding EOD Ingestor Datastore")
    db = SessionLocal()
    db.add(
        EodIngestorDataStoreModel(
            name=os.getenv("EOD_INGESTOR_DATASTORE_NAME"),
            url=os.getenv("EOD_INGESTOR_DATASTORE_URL"),
            container="eod",
            subscription_id=os.getenv("EOD_INGESTOR_DATASTORE_SUBSCRIPTION_ID"),
        )
    )
    db.commit()


def main():
    """Main function"""
    logger.info("Starting Seeding EOD Ingestor")

    # seed_timezones()
    # seed_currencies()
    # seed_countries()
    # seed_cities()
    # seed_exchanges()
    # seed_tickers()
    # seed_eod_ingestor_datastore()

    logger.info("EOD Ingestor finished")


main()
