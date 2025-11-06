import os
import uuid
import logging
from typing import Any
from google.adk.tools.tool_context import ToolContext
from google.genai import types as gt


logger = logging.getLogger(__name__)

MAX_BYTES_PDF = 5 * 1024 * 1024  # 5 MB
MAX_BYTES_JPEG = 2 * 1024 * 1024  # 2 MB
TOTAL_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_FILES_ALLOWED = 5

def _obtain_part_and_name(
        content: gt.Content | None, rid: str
) -> list[tuple[gt.Part | None, str | None]]:
    if not content or not content.parts:
        return []
    result: list[tuple[gt.Part | None, str | None]] = []
    for p in content.parts:
        if getattr(p, "inline_data", None) and p.inline_data and p.inline_data.data:
            result.append((p, p.inline_data.display_name))
        elif (
                getattr(p, "file_data", None) and p.file_data and getattr(p.file_data, "file_uri", None)
        ):
            result.append((p, getattr(p.file_data, "display_name", None)))
    return result


async def _bytes_from_any(part: gt.Part, tool_context: ToolContext) -> bytes:
    if getattr(part, "inline_data", None) and part.inline_data and part.inline_data.data:
        return part.inline_data.data
    if (
            getattr(part, "file_data", None)
            and part.file_data
            and getattr(part.file_data, "file_uri", None)
    ):
        loader = getattr(tool_context, "load_artifact_bytes", None)
        if callable(loader):
            return await loader(part.file_data.file_uri)  # type: ignore[reportUnknownVariableType]
        raise ValueError("file_data present but tool_context.load_artifact_bytes is unavailable.")
    raise ValueError("Part has no inline_data or file_data.")


def _preliminary_part_checks(parts: list[Any], rid: str) -> dict[str, Any] | None:
    if len(parts) == 0:
        return {
            "status": "failure",
            "message": "No file found in the message. Attach a PDF and send it in the same message.",
            "rid": rid,
        }
    if len(parts) > MAX_FILES_ALLOWED:
        return {
            "status": "failure",
            "message": f"Too many files. Send at most {MAX_FILES_ALLOWED} files.",
            "rid": rid,
        }
    return None



def handle_files_tool(
        filename: str,
        data_type: str,
) -> dict[str, Any]:

    s3_bucket = os.getenv("S3_BUCKET_NAME")
    if not s3_bucket:
        logger.error("S3_BUCKET_NAME environment variable not set.")
        return {"status": "failure", "message": "S3 bucket name not configured."}

    if data_type == 'is_pdf':
        directory = 'pdfs'
    if data_type == 'is_data':
        directory = 'data'
    if data_type == 'is_image':
        directory = 'images'

    try:
        s3 = boto3.client("presentations")
        s3_key = f"{directory}/{filename}"

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        object_data = response['Body'].read()

        logger.info(f"Successfully retrieved {s3_key} from S3 bucket {s3_bucket}.")

        return {
            "status": "success",
            "filename": filename,
            "data_type": data_type,
            "object_data": object_data
        }

    except (NoCredentialsError, PartialCredentialsError):
        logger.error("S3 credentials not found.")
        return {"status": "failure", "message": "S3 credentials not found."}
    except s3.exceptions.NoSuchKey:
        logger.error(f"File not found in S3: {s3_key}")
        return {"status": "failure", "message": f"File not found: {filename}"}
    except BotoCoreError as e:
        logger.error(f"S3 download failed: {e}")
        return {"status": "failure", "message": f"S3 download failed: {e}"}
    except Exception as e:
        logger.exception("Failed to retrieve file from S3.")
        return {"status": "failure", "message": f"Failed to retrieve file: {e!s}"}