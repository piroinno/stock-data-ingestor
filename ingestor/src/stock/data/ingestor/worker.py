import base64
import datetime
from distutils.util import strtobool
import json
import math
import requests
import logging
import os
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.queue import (
    QueueClient,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_PARAMS = {"access_key": os.getenv("MARKETSTACK_API_KEY"), "limit": 1000}
MAX_PAGES = 1000
MARKETSTACK_API = "http://api.marketstack.com/v1"


def get_requests_with_offset(endpoint, initial_offset=1, extra_params={}):
    offset = initial_offset
    data = []
    logger.info("Getting data from Marketstack API for endpoint: %s", endpoint)
    while True:
        _data = requests.get(
            f"{MARKETSTACK_API}/{endpoint}",
            params={**DEFAULT_PARAMS, "offset": offset, **extra_params},
        ).json()
        if(_data.get("data") is not None):
            data.extend(_data["data"])

        if(_data.get("pagination") is not None):
            if (
                offset >= MAX_PAGES or offset >= math.ceil(_data["pagination"]["total"] / DEFAULT_PARAMS["limit"])
            ):
                break
        else:
            break
        
        offset += 1

    return {"data": remove_dupes(data)}


def remove_dupes(data):
    new_d = []
    for x in data:
        if x not in new_d:
            new_d.append(x)
    return new_d


def chunk_list(data, chunksize):
    for i in range(0, len(data), chunksize):
        yield data[i : i + chunksize]


def get_ext_eod_exchange(tickers_str, exchange_mic, date=None):
    """Get EOD data for an exchange from Marketstack API"""
    logger.info("Get EOD data for an exchange from Marketstack API")
    logger.info("First, get the list of tickers for the exchange")
    tickers = tickers_str.split(",")
    eod_data = []
    logger.info("Then, get the EOD data for tickers. Max is 100")
    for ticker_chunks in chunk_list(tickers, 100):
        extra_params = {
            "symbols": ",".join([ticker_chunk for ticker_chunk in ticker_chunks])
        }
        if date is not None:
            eod_data.extend(
                get_requests_with_offset(f"eod/{date}", 0, extra_params)["data"]
            )
        else:
            eod_data.extend(
                get_requests_with_offset(f"eod/latest", 0, extra_params)["data"]
            )

    return {"data": eod_data}


def configure_eod_ingestor_datastore_auth(storage_name, file_system):
    """Get auth for EOD Ingestor Datastore"""
    logger.info("Getting auth for EOD Ingestor Datastore")
    global adls_service_client
    default_credential = DefaultAzureCredential()
    adls_service_client = DataLakeServiceClient(
        account_url="{}://{}.dfs.core.windows.net".format(
            "https", storage_name, file_system
        ),
        credential=default_credential,
    )


def configure_eod_ingestor_worker_auth(storage_name, queue_name):
    """Get auth for EOD Ingestor Controller"""
    logger.info("Getting auth for EOD Ingestor Controller")
    global queue_service_client
    default_credential = DefaultAzureCredential()
    queue_service_client = QueueClient(
        account_url="{}://{}.queue.core.windows.net".format("https", storage_name),
        credential=default_credential,
        queue_name=queue_name,
        message_encode_policy=BinaryBase64EncodePolicy(),
        message_decode_policy=BinaryBase64DecodePolicy(),
    )


def save_eod(
    file_name_preffix,
    eod_data,
    file_system,
    eod_ingestor_datastore_name,
):
    """Save EOD data for an exchange"""
    logger.info("Saving EOD data for an exchange")
    eod_ingestor_datastore = {
        "name": eod_ingestor_datastore_name,
    }
    configure_eod_ingestor_datastore_auth(eod_ingestor_datastore_name, file_system)

    for eod in eod_data["data"]:
        file_name = f"{file_name_preffix}/{eod['symbol']}.json"
        file_content = json.dumps(eod)
        file_system_client = adls_service_client.get_file_system_client(file_system)
        file_client = file_system_client.get_file_client(file_name)
        file_client.create_file()
        file_client.append_data(data=file_content, offset=0, length=len(file_content))
        file_client.flush_data(len(file_content))


def log_eod_ingestor_worker_status(
    success_file_contents, file_name_preffix, file_system
):
    """Log EOD Ingestor Worker status"""
    logger.info("Logging EOD Ingestor Worker status")
    file_name = f"{file_name_preffix}/EODSTATUS.json"
    file_system_client = adls_service_client.get_file_system_client(file_system)
    file_client = file_system_client.get_file_client(file_name)
    file_client.create_file()
    file_client.append_data(
        data=success_file_contents, offset=0, length=len(success_file_contents)
    )
    file_client.flush_data(len(success_file_contents))


def process_messages():
    logger.info("Getting messages from queue")
    properties = queue_service_client.get_queue_properties()
    if properties.approximate_message_count > 0:
        messages = queue_service_client.receive_messages(
            messages_per_page=1, visibility_timeout=5 * 60
        )
        for msg_batch in messages.by_page():
            for msg in msg_batch:
                # try:
                message = json.loads(base64.b64decode(msg.content).decode("utf-8"))
                file_system = message["eod_datastore_container"]
                eod_data = get_ext_eod_exchange(
                    message["tickers"], message["exchange_mic"], message["date"]
                )
                if strtobool(message["partition_by_date"]):
                    logger.info("Partitioning by date")
                    file_name_preffix = f'{message["date"]}/{message["exchange_mic"]}'
                else:
                    file_name_preffix = f'{message["exchange_mic"]}/{message["date"]}'

                save_eod(
                    file_name_preffix,
                    eod_data,
                    file_system,
                    message["eod_datastore_name"],
                )
                success_file_contents = json.dumps(
                    {
                        "status": "success",
                        "message": "EOD data ingested successfully",
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_name_preffix": file_name_preffix,
                    },
                    indent=4,
                )
                log_eod_ingestor_worker_status(
                    success_file_contents, file_name_preffix, file_system
                )
                queue_service_client.delete_message(msg)
                # except Exception as e:
                #   logger.warning(f"Error processing message: {e}")


def main():
    """Main function"""
    logger.info("Starting EOD Ingestor")
    configure_eod_ingestor_worker_auth(
        os.getenv("EOD_INGESTOR_STROAGE_NAME"), os.getenv("EOD_INGESTOR_STROAGE_QUEUE")
    )
    process_messages()

    logger.info("EOD Ingestor finished")
    
if __name__ == "__main__":
    main()
