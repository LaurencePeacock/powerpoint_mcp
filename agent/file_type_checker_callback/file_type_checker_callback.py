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

    user = None
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            user = content
            break

    is_pdf = False
    is_image = False
    is_data = False
    mime_types: set[str] = set()

    if user and user.parts:
        for p in user.parts:
            idata = getattr(p, "inline_data", None)

            if idata and idata.data:
                mt = (idata.mime_type or "").lower()
                if mt:
                    mime_types.add(mt)
                if pdf_type_checker(p):
                    is_pdf = True
                if image_type_checker(p):
                    is_image = True
                if data_type_checker(p):
                    is_data = True


    # Checks file size against configured limits
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
    MAX_DATA_SIZE = 10 * 1024 * 1024  # 10MB

    if user and user.parts:
        for p in user.parts:
            file_size = 0
            idata = getattr(p, "inline_data", None)
            # fdata = getattr(p, "file_data", None)

            if idata and idata.data:
                file_size = len(idata.data)

            if file_size > 0:
                if image_type_checker(p) and file_size > MAX_IMAGE_SIZE:
                    return LlmResponse(
                        contents=[
                            gt.Content(
                                role="model",
                                parts=[
                                    gt.Part(
                                        text="[ERROR]\nImage file size exceeds the limit of 2MB."
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

    # saves approved attachments to local directory
        if is_pdf or is_image or is_data:
            try:

                file_name = uuid.uuid4().hex[:16]
                for extension in mime_types:
                    file_extension = extension.split("/")[1]
                data = p.inline_data.data

                file_storage_path = "file_storage"
                file_path = os.path.join(file_storage_path, f"{file_name}.{file_extension}")
                with open(file_path, "wb") as f:
                    f.write(data)

            except Exception as e:
                logger.exception("Failed to save  name=%s", file_name, )
                return {"status": "failure", "message": f"Failed to save file: {e!s}", "file_name": file_name}


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
