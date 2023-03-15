import base64
import datetime
import json

import pytz
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import (
    QueueClient,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)
from stock.data.model.database import SessionLocal
from stock.data.model.crud import (
    get_eod_ingestor_data_store,
    get_exchanges,
    get_ticker_by_exchange,
    get_timezone,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_eod_ingestor_controller_auth(storages_name, queue_name):
    """Get auth for EOD Ingestor Controller"""
    logger.info("Getting auth for EOD Ingestor Controller")
    global queue_service_client
    default_credential = DefaultAzureCredential()
    queue_service_client = QueueClient(
        account_url="{}://{}.queue.core.windows.net".format("https", storages_name),
        credential=default_credential,
        queue_name=queue_name,
        message_encode_policy=BinaryBase64EncodePolicy(),
        message_decode_policy=BinaryBase64DecodePolicy(),
    )


def add_message_to_queue(message):
    """Add message to queue"""
    logger.info("Adding message to queue")
    queue_service_client.send_message(base64.b64encode(json.dumps(message).encode()))


def create_job_messages(db, exchanges):
    logger.info("Creating job messages")
    eod_datastore = get_eod_ingestor_data_store(db, os.getenv("EOD_DATASTORE_ID"))
    for exchange in exchanges:
        tickers = get_ticker_by_exchange(db, exchange.id)
        if len(tickers) == 0:
            continue
        logger.info("Processing exchange: {}".format(exchange.name))
        message = {
            "exchange": exchange.name,
            "exchange_mic": exchange.mic,
            "date": datetime.datetime.now(pytz.timezone(get_timezone(db, exchange.timezone_id).name)).strftime("%Y-%m-%d"),
            "type": "EOD",
            "eod_datastore_id": os.getenv("EOD_DATASTORE_ID"),
            "eod_datastore_name": eod_datastore.name,
            "eod_datastore_container": eod_datastore.container,
            "partition_by_date": "true",
            "tickers": ",".join([ticker.ticker for ticker in tickers]),
        }
        add_message_to_queue(message)


def main():
    logger.info("Starting EOD Ingestor Controller")
    db = SessionLocal()
    exchanges = get_exchanges(db)
    configure_eod_ingestor_controller_auth(
        os.getenv("EOD_INGESTOR_STROAGE_NAME"),
        os.getenv("EOD_INGESTOR_STROAGE_QUEUE"),
    )
    create_job_messages(db, exchanges)
    logger.info("EOD Ingestor Controller finished")


