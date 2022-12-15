import boto3


def compare_face(cnic: bytes, selfie: bytes):

    rekognition_client = boto3.client("rekognition")

    try:
        response = rekognition_client.compare_faces(
            SourceImage={"Bytes": selfie.decode().encode("latin-1")},
            TargetImage={"Bytes": cnic.decode().encode("latin-1")},
            SimilarityThreshold=95,
        )

        if response["FaceMatches"]:
            return True

        return False
    except:
        return False
