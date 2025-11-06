from google.genai import types as gt

def _looks_like_pdf(b: bytes) -> bool:
    head = b[:8].lstrip()
    return head.startswith(b"%PDF-")

def pdf_type_checker(part: gt.Part) -> bool:
    if getattr(part, "inline_data", None) and part.inline_data and part.inline_data.data:
        data = part.inline_data.data
        if part.inline_data.mime_type == "application/pdf":
            return True
        dn = (part.inline_data.display_name or "").lower()
        if dn.endswith(".pdf"):
            return True
        return bool(_looks_like_pdf(data))
    if getattr(part, "file_data", None) and part.file_data:
        mt = (getattr(part.file_data, "mime_type", "") or "").lower()
        dn = (getattr(part.file_data, "display_name", "") or "").lower()
        if mt == "application/pdf" or dn.endswith(".pdf"):
            return True
    return False


def _is_jpeg_part(part: gt.Part) -> bool:
    if getattr(part, "inline_data", None) and part.inline_data:
        if part.inline_data.mime_type == "image/jpeg":
            return True
        dn = (part.inline_data.display_name or "").lower()
        if dn.endswith(".jpg") or dn.endswith(".jpeg"):
            return True
    if getattr(part, "file_data", None) and part.file_data:
        mt = (getattr(part.file_data, "mime_type", "") or "").lower()
        dn = (getattr(part.file_data, "display_name", "") or "").lower()
        if mt == "image/jpeg" or dn.endswith(".jpg") or dn.endswith(".jpeg"):
            return True
    return False


def image_type_checker(part: gt.Part) -> bool:
    """Checks if the part is a JPEG or PNG image."""
    # Check for inline_data
    if getattr(part, "inline_data", None) and part.inline_data:
        mime_type = part.inline_data.mime_type
        display_name = (part.inline_data.display_name or "").lower()

        # Check MIME type and file extension
        if mime_type in ("image/jpeg", "image/png") or display_name.endswith((".jpg", ".jpeg", ".png")):
            return True

    # Check for file_data
    if getattr(part, "file_data", None) and part.file_data:
        mime_type = (getattr(part.file_data, "mime_type", "") or "").lower()
        display_name = (getattr(part.file_data, "display_name", "") or "").lower()

        # Check MIME type and file extension
        if mime_type in ("image/jpeg", "image/png") or display_name.endswith((".jpg", ".jpeg", ".png")):
            return True
    return False


def data_type_checker(part: gt.Part) -> bool:
    """Checks if the part is an Excel spreadsheet or a CSV file."""
    # Define accepted MIME types for spreadsheets and CSVs
    accepted_mime_types = (
        "text/csv",
        "application/vnd.ms-excel",  # For .xls files
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # For .xlsx files
    )

    # Define accepted file extensions
    accepted_extensions = (".csv", ".xls", ".xlsx")

    # Check for inline_data
    if getattr(part, "inline_data", None) and part.inline_data:
        mime_type = part.inline_data.mime_type
        display_name = (part.inline_data.display_name or "").lower()

        if mime_type in accepted_mime_types or display_name.endswith(accepted_extensions):
            return True

    # Check for file_data
    if getattr(part, "file_data", None) and part.file_data:
        mime_type = (getattr(part.file_data, "mime_type", "") or "").lower()
        display_name = (getattr(part.file_data, "display_name", "") or "").lower()

        if mime_type in accepted_mime_types or display_name.endswith(accepted_extensions):
            return True

    return False