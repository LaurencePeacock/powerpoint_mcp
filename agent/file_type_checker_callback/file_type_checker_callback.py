import logging
import os
import uuid
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as gt
from google.adk.models import LlmResponse, LlmRequest
from agent.file_type_checker_callback.type_checker_utils import pdf_type_checker, image_type_checker, data_type_checker

logger = logging.getLogger(__name__)

def file_type_checker_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> LlmResponse | None:

    # Find last user turn
    user = None
    for c in reversed(llm_request.contents or []):
        if c.role == "user":
            user = c
            break

    # files = 0
    is_pdf = False
    # has_jpeg = False
    is_image = False
    is_data = False
    mime_types: set[str] = set()

    if user and user.parts:
        for p in user.parts:
            idata = getattr(p, "inline_data", None)
            fdata = getattr(p, "file_data", None)

            if idata and idata.data:
                # files += 1
                mt = (idata.mime_type or "").lower()
                if mt:
                    mime_types.add(mt)
                if pdf_type_checker(p):
                    is_pdf = True
                if image_type_checker(p):
                    is_image = True
                if data_type_checker(p):
                    is_data = True
            elif fdata and getattr(fdata, "file_uri", None):
                # files += 1
                mt = (getattr(fdata, "mime_type", "") or "").lower()
                if mt:
                    mime_types.add(mt)
                if pdf_type_checker(p):
                    is_pdf = True
                if image_type_checker(p):
                    is_image = True
                if data_type_checker(p):
                    is_data = True

    # Checks file size against configured limits
    MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 3MB
    MAX_DATA_SIZE = 10 * 1024 * 1024  # 10MB

    if user and user.parts:
        for p in user.parts:
            file_size = 0
            idata = getattr(p, "inline_data", None)
            fdata = getattr(p, "file_data", None)

            if idata and idata.data:
                file_size = len(idata.data)
            elif fdata and getattr(fdata, "file_uri", None):
                file_path = getattr(fdata, "file_uri", "").replace("file://", "")
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)

            if file_size > 0:
                if image_type_checker(p) and file_size > MAX_IMAGE_SIZE:
                    return LlmResponse(
                        contents=[
                            gt.Content(
                                role="model",
                                parts=[
                                    gt.Part(
                                        text="[ERROR]\nImage file size exceeds the limit of 3MB."
                                    )
                                ],
                            )
                        ]
                    )
                if data_type_checker(p) and file_size > MAX_DATA_SIZE:
                    return LlmResponse(
                        contents=[
                            gt.Content(
                                role="model",
                                parts=[
                                    gt.Part(
                                        text="[ERROR]\nData file size exceeds the limit of 10MB."
                                    )
                                ],
                            )
                        ]
                    )

    # saves approved attachments to S3 bucket
        if is_pdf or is_image or is_data:
            try:

                file_name = uuid.uuid4().hex[:16]
                for extension in mime_types:
                    file_extension = extension.split("/")[1]
                data = p.inline_data.data

                # S3 Upload
                s3_bucket = os.getenv("S3_BUCKET_NAME")
                if s3_bucket:
                    try:
                        s3 = boto3.client("presentations")
                        s3_key = ""
                        if is_pdf:
                            s3_key = f"pdfs/{file_name}.{file_extension}"
                        elif is_image:
                            s3_key = f"images/{file_name}.{file_extension}"
                        elif is_data:
                            s3_key = f"data/{file_name}.{file_extension}"

                        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)
                        logger.info(f"Successfully uploaded {s3_key} to S3 bucket {s3_bucket} at key {s3_key}")
                    except (NoCredentialsError, PartialCredentialsError):
                        logger.error("S3 credentials not found. Skipping upload.")
                    except BotoCoreError as e:
                        logger.error(f"S3 upload failed: {e}")
            except Exception as e:
                logger.exception("Failed to save  name=%s", file_name, )
                return {"status": "failure", "message": f"Failed to save artifact: {e!s}", "file_name": file_name}


            meta = (
                f"""[FILE ATTACHMENT]
                mime_types = {','.join(sorted(mime_types)) if mime_types else 'unknown'}
                file_name = '{file_name}.{file_extension}'
                is_pdf = {'true' if is_pdf else 'false'}
                is_image = {'true' if is_image else 'false'}
                is_data = {'true' if is_data else 'false'}"""
            )

    llm_request.contents = llm_request.contents or []
    if is_pdf or is_image or is_data:
        llm_request.contents.insert(0, gt.Content(role="model", parts=[gt.Part(text=meta)]))

    return None