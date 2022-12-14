import boto3


def analyze_id(cnic_bytes: bytes):
    textract_client = boto3.client("textract")
    response = textract_client.detect_document_text(Document={"Bytes": cnic_bytes})
    print(response)
