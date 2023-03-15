import pytest
from unittest.mock import patch
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._models import ContentSettings
from azure.core._match_conditions import MatchConditions
from azure.identity import DefaultAzureCredential
from src.stock.data.ingestor.worker import (
    get_ext_eod_exchange,
    get_requests_with_offset,
)


def test_get_requests_with_offset():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": [{"a": 1}, {"a": 2}],
            "pagination": {"count": 2},
        }
        result = get_requests_with_offset(
            endpoint="eod/XNAS/2020-01-01",
            initial_offset=0,
            extra_params={"symbols": "AAPL,GOOG", "limit": 1000},
        )
        assert result == {"data": [{"a": 1}, {"a": 2}]}


def test_get_ext_eod_exchange():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": [{"a": 1}, {"a": 2}],
            "pagination": {"count": 2},
        }
        result = get_ext_eod_exchange("AAPL,GOOG", "XNAS")
        assert result == {"data": [{"a": 1}, {"a": 2}]}


def test_get_ext_eod_exchange_with_date():
    with patch("src.stock.data.ingestor.worker.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {
            "data": [{"a": 1}, {"a": 2}],
            "pagination": {"count": 2},
        }
        result = get_ext_eod_exchange(
            "AAPL,GOOG", "XNAS", "2020-01-01"
        )
        assert result == {"data": [{"a": 1}, {"a": 2}]}