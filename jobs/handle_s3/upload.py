import boto3
from PIL import Image
from io import BytesIO
import magic

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

s3 = boto3.client("s3")


async def s3_upload(contents: bytes, key: str):
    s3.put_object(Body=contents, Bucket=AWS_BUCKET, Key=key)


async def upload_file(path, file=None, file_bytes=None):
    try:
        if file:
            file_bytes = await file.read()
        if not file_bytes:
            raise ValueError("No file content provided.")

        file_type = magic.from_buffer(file_bytes, mime=True)

        if file_type not in SUPPORTED_FILE_TYPES:
            return ErrorsService().bad_request(
                loc="body", value="file", msg="File type not supported"
            )

        if file_type.startswith("image"):
            image = Image.open(BytesIO(file_bytes))
            image = image.convert("RGB")
            image_io = BytesIO()
            image.save(image_io, "JPEG", quality=80)
            compressed_file = image_io.getvalue()

        elif file_type == "application/pdf":
            compressed_file = file_bytes

        await s3_upload(compressed_file, f"{PATH}{path}")

        return True

    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)
