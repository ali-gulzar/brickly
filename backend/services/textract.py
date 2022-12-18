import boto3

from database.model import DBUser


def analyze_id(cnic: bytes, current_user: DBUser):
    textract_client = boto3.client("textract")
    response = textract_client.analyze_document(
        Document={"Bytes": cnic.decode().encode("latin-1")}, FeatureTypes=["FORMS"]
    )

    for data in response["Blocks"]:
        if (
            data["BlockType"] == "WORD"
            and data["Text"].replace("-", "") == current_user.cnic_number
        ):
            return True
    return False
