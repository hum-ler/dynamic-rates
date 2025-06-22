import boto3
import json
import logging
import os
import urllib3
from botocore.exceptions import ClientError
from datetime import datetime
from zoneinfo import ZoneInfo

from currencies import CURRENCIES

logger = logging.getLogger()

# Environment variables.
API_BASE_URL = "API_BASE_URL"
API_KEY = "API_KEY"
DYNAMODB_TABLE = "DYNAMODB_TABLE"
LOG_LEVEL = "LOG_LEVEL"


def fetch_data_from_api(api_base_url, api_key):
    symbols = ",".join(CURRENCIES.keys())

    api_endpoint = f"{api_base_url}/latest?access_key={api_key}&symbols={symbols}"
    logger.info(f"Calling API endpoint: {api_base_url}/latest?symbols={symbols}")

    http = urllib3.PoolManager()
    response = http.request("GET", api_endpoint)
    if response.status != 200:
        error_message = f"API call failed with status code {response.status}: {response.data.decode('utf-8')}"
        logger.error(f"Error: {error_message}")
        raise ValueError(error_message)

    try:
        api_data = json.loads(response.data.decode("utf-8"))
        logger.info("Successfully retrieved and parsed data from API.")
        logger.debug(f"Parsed data: {api_data}")
        return api_data
    except json.JSONDecodeError as e:
        logger.exception(f"Error: Failed to decode JSON from API response. {e}")
        raise ValueError("Invalid JSON format received from the external API.") from e


def reformat_item_for_dynamodb(api_data):
    try:
        timestamp = datetime.fromtimestamp(
            api_data["timestamp"], tz=ZoneInfo("Asia/Singapore")
        ).isoformat()
        item = {
            "rates-id": {"S": timestamp},
            "timestamp": {"S": timestamp},
            "base-currency": {"S": api_data["base"]},
            "data": {
                "L": [
                    {
                        "M": {
                            "code": {"S": code},
                            "symbol": {"S": CURRENCIES[code]["symbol"]},
                            "name": {"S": CURRENCIES[code]["name"]},
                            "exchange-rate": {"N": str(api_data["rates"][code])},
                            "precision": {"N": str(CURRENCIES[code]["precision"])},
                            "region-emoji": {"S": CURRENCIES[code]["region-emoji"]},
                        }
                    }
                    for code in api_data["rates"]
                    if code in CURRENCIES
                ]
            },
        }
        logger.debug(f"Reformatted item: {json.dumps(item)}")
        return item
    except KeyError as e:
        logger.error(f"Error: JSON reformatting failed due to missing key: {str(e)}")
        raise KeyError(
            f"Failed to reformat JSON. Missing expected key: {str(e)}"
        ) from e


def store_item_in_dynamodb(table_name, item):
    try:
        # Boto3 will automatically use the IAM role credentials from the Lambda environment.
        dynamodb = boto3.client("dynamodb")
        dynamodb.put_item(TableName=table_name, Item=item)
        logger.info(
            f"Successfully ingested timestamped item into DynamoDB table: {table_name}"
        )

        # Overwrite the latest rates.
        item["rates-id"] = {"S": "latest-rates"}
        dynamodb.put_item(TableName=table_name, Item=item)
        logger.info(
            f"Successfully updated 'latest-rates' item in DynamoDB table: {table_name}"
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        logger.exception(
            f"Error putting item into DynamoDB: {error_code} - {error_message}"
        )
        raise


def lambda_handler(event, context):
    # Get environment variables.
    try:
        api_base_url = os.environ[API_BASE_URL]
        api_key = os.environ[API_KEY]
        dynamodb_table = os.environ[DYNAMODB_TABLE]
        log_level = os.environ[LOG_LEVEL]
    except KeyError as e:
        logger.exception(f"Error: Missing environment variable {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                f"Configuration error: Missing environment variable {str(e)}"
            ),
        }

    # Set up the logger.
    logger.setLevel(log_level)

    # Steps.
    try:
        raw_data = fetch_data_from_api(api_base_url, api_key)
        item_to_store = reformat_item_for_dynamodb(raw_data)
        store_item_in_dynamodb(dynamodb_table, item_to_store)
    except (ValueError, KeyError, ClientError, urllib3.exceptions.MaxRetryError) as e:
        # Catch exceptions from any of the steps and return an error response.
        return {"statusCode": 500, "body": json.dumps(f"Processing failed: {str(e)}")}
    except Exception as e:
        # Catch any other unexpected errors.
        logger.exception(f"An unexpected error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps("An unexpected error occurred during processing."),
        }

    # Report success.
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Data successfully processed and stored.",
                "itemId": item_to_store.get("UserID", "N/A"),
            }
        ),
    }
