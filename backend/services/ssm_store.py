import boto3
import os

OFFLINE = os.environ.get("OFFLINE") == "true"
ENVIRONMENT = os.environ["ENVIRONMENT"]

def get_parameter(parameter: str):
    if OFFLINE:
        return os.environ[parameter]

    client = boto3.client('ssm')
    value = client.get_parameter(Name=f'/brickly-backend-{ENVIRONMENT}/{parameter}', WithDecryption=True)['Parameter']['Value']
    return value
