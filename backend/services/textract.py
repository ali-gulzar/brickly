import boto3

from models.common import TextractAPIResponse
from models.database import DBUser


def analyze_id(cnic: bytes, current_user: DBUser):
    textract_client = boto3.client("textract")
    response = textract_client.analyze_id(
        DocumentPages=[{"Bytes": cnic.decode().encode("latin-1")}]
    )

    # look for DOCUMENT_NUMBER value in response
    for data in response["IdentityDocuments"][0]["IdentityDocumentFields"]:
        if data["Type"]["Text"] == TextractAPIResponse.document_number:
            found_text_value: str = data["ValueDetection"]["Text"]
            if found_text_value.replace("-", "") == current_user.cnic_number:
                return True
            return False
