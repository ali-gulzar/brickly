import os
from random import randint

import boto3

from services import dynamo

OFFLINE = os.environ.get("OFFLINE") == "true"


def get_sns_client():
    if OFFLINE:
        return boto3.client("sns", endpoint_url="http://localhost:4002")
    else:
        return boto3.client("sns")


def generate_otp(phone_number: str):
    otp = randint(1000, 9999)

    # Send SMS
    sns_client = get_sns_client()
    sns_client.publish(
        PhoneNumber=f"+92{phone_number[1:]}",
        Message=f"This is your OTP {otp}.",
        MessageAttributes={
            "SMSType": {"DataType": "String", "StringValue": "Transactional"}
        },
    )

    # add otp to dynamodb
    dynamo.add_otp(phone_number, otp)

    return otp
