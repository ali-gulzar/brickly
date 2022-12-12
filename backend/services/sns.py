import boto3
from random import randint
from services.dynamo import add_otp

def generate_otp(phone_number: str):
    otp = randint(1000, 9999)

    # Send SMS
    sns_client = boto3.client('sns')
    sns_client.publish(
        PhoneNumber = phone_number,
        Message = f"This is your OTP {otp}.",
        MessageAttributes = {
            'SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}
        }
    )

    # add otp to dynamodb
    add_otp(phone_number, otp)


    return otp


