import os
import pytest
from unittest.mock import patch
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._models import ContentSettings
from azure.core._match_conditions import MatchConditions
from azure.storage.queue import (
    QueueClient,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)
from azure.identity import DefaultAzureCredential
from src.stock.data.ingestor.worker import (
    get_ext_eod_exchange,
    get_requests_with_offset,
)
from stock.data.model import crud
from stock.data.model import models
from src.stock.data.ingestor.controller import create_job_messages
from stock.data.model.database import SessionLocal, engine, Base


def init_test_db():
    Base.metadata.create_all(bind=engine)


def drop_test_db():
    Base.metadata.drop_all(bind=engine)


def recreate_test_db():
    drop_test_db()
    init_test_db()


@pytest.fixture(scope="session")
def db():
    recreate_test_db()
    db = SessionLocal()
    add_timezone(db)
    add_country(db)
    add_city(db)
    add_exchanges(db)
    add_ticker(db)
    add_eod_data_store(db)
    try:
        yield db
    finally:
        db.close()


def add_timezone(db: SessionLocal):
    # Add test data
    crud.set_timezone(
        db,
        timezone=models.TimezoneModel(
            name="Eastern Standard Time", abbr="EST", dst="EDT"
        ),
    )

    crud.set_timezone(
        db,
        timezone=models.TimezoneModel(
            name="Greenwich Mean Time", abbr="GMT", dst="BST"
        ),
    )


def add_city(db: SessionLocal):
    # Add test data
    crud.set_city(db, city=models.CityModel(name="New York", country_id=1))

    crud.set_city(db, city=models.CityModel(name="London", country_id=2))


def add_country(db: SessionLocal):
    # Add test data
    crud.set_country(db, country=models.CountryModel(name="United States", code="US"))

    crud.set_country(db, country=models.CountryModel(name="United Kingdom", code="UK"))


def add_ticker(db: SessionLocal):
    # Add test data
    crud.set_ticker(
        db, ticker=models.TickerModel(ticker="AAPL", name="Apple Inc.", exchange_id=1)
    )


def add_exchanges(db: SessionLocal):
    # Add test data
    crud.set_exchange(
        db,
        exchange=models.ExchangeModel(
            name="National Association of Securities Dealers Automated Quotations",
            country_id=1,
            city_id=1,
            timezone_id=1,
            acronym="NASDAQ",
            mic="XNAS",
        ),
    )

    crud.set_exchange(
        db,
        exchange=models.ExchangeModel(
            name="New York Stock Exchange",
            country_id=1,
            city_id=1,
            timezone_id=1,
            acronym="NYSE",
            mic="XNYS",
        ),
    )

    crud.set_exchange(
        db,
        exchange=models.ExchangeModel(
            name="London Stock Exchange",
            country_id=2,
            city_id=2,
            timezone_id=2,
            acronym="LSE",
            mic="XLON",
        ),
    )


def add_eod_data_store(db: SessionLocal):
    # Add test data
    os.environ["EOD_DATASTORE_ID"] = "1"
    crud.set_eod_ingestor_data_store(
        db,
        models.EodIngestorDataStoreModel(
            name="eod",
            url="https://eod.dfs.core.windows.net",
            subscription_id="test",
            container="eod",
            tenant_id="test",
        ),
    )


def test_get_requests_with_offset():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": {"eod": [{"a": 1}, {"a": 2}]},
            "pagination": {"count": 2, "total": 1},
        }
        result = get_requests_with_offset(
            endpoint="exchanges/XNAS/eod/2020-01-01",
            initial_offset=0,
            extra_params={"symbols": "AAPL,GOOG", "limit": 1000},
        )
        assert result == [{"a": 1}, {"a": 2}]


def test_get_ext_eod_exchange():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": {"eod": [{"a": 1}, {"a": 2}]},
            "pagination": {"count": 2},
        }
        result = get_ext_eod_exchange("AAPL,GOOG", "XNAS")
        assert result == [{"a": 1}, {"a": 2}]


def test_get_ext_eod_exchange_with_date():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": {"eod": [{"a": 1}, {"a": 2}]},
            "pagination": {"count": 2},
        }
        result = get_ext_eod_exchange("AAPL,GOOG", "XNAS", "2020-01-01")
        assert result == [{"a": 1}, {"a": 2}]


def test_create_job_messages(db: SessionLocal):
    with patch(
        "src.stock.data.ingestor.controller.create_job_messages"
    ) as mock_create_job_messages:
        mock_create_job_messages.return_value = None
        assert (
            create_job_messages(
                db,
                [
                    models.ExchangeModel(
                        name="XNAS",
                        acronym="NASDAQ",
                        mic="XNAS",
                        country_id=1,
                        city_id=1,
                        timezone_id=1,
                    )
                ],
            )
            == None
        )
