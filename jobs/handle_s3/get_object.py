import boto3
import base64

from services.auth.ErrorsService import ErrorsService
from utils.settings import Settings

settings = Settings()

SUPPORTED_FILE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/jpg": "jpg",
    "application/pdf": "pdf",
}

AWS_BUCKET = settings.aws_bucket
PATH = settings.aws_path

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")


async def get_file_64(path: str):
    try:
        obj = s3.Object(AWS_BUCKET, f"{PATH}{path}")

        file = base64.b64encode(obj.get()["Body"].read())
        file = file.decode("ascii")

        return file

    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)


async def get_link_download(path: str):
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": AWS_BUCKET, "Key": f"{PATH}{path}"},
            ExpiresIn=3600,  # La URL expirará en 1 hora
        )

        return url

    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)
