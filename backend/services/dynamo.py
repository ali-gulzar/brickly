import boto3
import time


def verify_otp(phone_number: str, otp: str):
    dynamo_client = boto3.client('dynamodb')
    item = dynamo_client.get_item(
        TableName = "OTP",
        Key = {"id": {"S": phone_number}}
    )
    db_otp = item["Item"]["otp"]["S"]

    return otp == db_otp


def add_otp(phone_number: str, otp: str):
    dynamo_client = boto3.client('dynamodb')
    dynamo_client.put_item(
        TableName='OTP',
        Item = {
            'id': {'S': phone_number},
            'otp': {'S': str(otp)},
            'ttl': {'N': str(180 + int(round(time.time())))}
        }
    )