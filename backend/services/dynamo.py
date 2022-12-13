import os
import time

import boto3

OFFLINE = os.environ.get("OFFLINE") == "true"


def get_dynamo_db_client():
    if OFFLINE:
        return boto3.client("dynamodb", endpoint_url="http://localhost:8000")
    else:
        return boto3.client("dynamodb")


def verify_otp(phone_number: str, otp: str):
    dynamo_client = get_dynamo_db_client()
    item = dynamo_client.get_item(TableName="OTP", Key={"id": {"S": phone_number}})
    db_otp = item["Item"]["otp"]["S"]

    return otp == db_otp


def add_otp(phone_number: str, otp: str):
    dynamo_client = get_dynamo_db_client()
    dynamo_client.put_item(
        TableName="OTP",
        Item={
            "id": {"S": phone_number},
            "otp": {"S": str(otp)},
            "ttl": {"N": str(180 + int(round(time.time())))},
        },
    )
