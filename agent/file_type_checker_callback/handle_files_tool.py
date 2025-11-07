import os
import logging
from typing import Any



logger = logging.getLogger(__name__)

MAX_BYTES_PDF = 5 * 1024 * 1024  # 5 MB
MAX_BYTES_JPEG = 2 * 1024 * 1024  # 2 MB
TOTAL_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_FILES_ALLOWED = 5


def handle_files_tool(
        filename: str,
        data_type: str,
) -> dict[str, Any]:

    file_path = os.path.join("file_storage", filename)

    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found in local storage: {file_path}")
            return {"status": "failure", "message": f"File not found: {filename}"}

        with open(file_path, "rb") as f:
            object_data = f.read()

        logger.info(f"Successfully retrieved {filename} from local file storage.")

        return {
            "status": "success",
            "filename": filename,
            "data_type": data_type,
            "object_data": object_data
        }

    except Exception as e:
        logger.exception(f"Failed to retrieve file from local storage: {filename}")
        return {"status": "failure", "message": f"Failed to retrieve file: {e!s}"}