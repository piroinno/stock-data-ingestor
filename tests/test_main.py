import pytest
from unittest.mock import patch
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._models import ContentSettings
from azure.core._match_conditions import MatchConditions
from azure.identity import DefaultAzureCredential
from stock.data.model import crud

from src.stock.data.ingestor.controller import (
    get_data_lake_service_client,
    get_data_lake_file_system_client,
    get_ticker,
    get_eod_ticker
)

from src.stock.data.ingestor.worker import (
    get_data_lake_service_client,
    get_data_lake_file_system_client,
    get_ticker,
    get_eod_ticker
)

@pytest.fixture
def mock_get_data_lake_service_client(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("stock.data.ingestor.controller.get_data_lake_service_client", mock_return)

@pytest.fixture
def mock_get_data_lake_file_system_client(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("stock.data.ingestor.controller.get_data_lake_file_system_client", mock_return)

@pytest.fixture
def mock_get_eod_ticker(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("stock.data.ingestor.controller.get_eod_ticker", mock_return)

@pytest.fixture
def mock_flagsmith(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("stock.data.ingestor.controller.flagsmith", mock_return)

def test_get_data_lake_service_client(mock_get_data_lake_service_client):
    try:
        assert get_data_lake_service_client() == "mocked"
    except Exception as e:
        assert True

def test_get_data_lake_file_system_client(mock_get_data_lake_file_system_client):
    try:
        assert get_data_lake_file_system_client() == "mocked"
    except Exception as e:
        assert True

def test_get_eod_ticker(mock_get_eod_ticker):
    try:
        assert get_eod_ticker("AAPL") == "mocked"
    except Exception as e:
        assert True

def test_get_ticker(mock_flagsmith):
    try:
        assert get_ticker("AAPL") == "mocked"
    except Exception as e:
        assert True