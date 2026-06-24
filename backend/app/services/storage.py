from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_UPLOAD_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}


def ensure_upload_directories() -> None:
    for child in ("submissions", "profile_images", "certificates", "projects"):
        (settings.UPLOAD_DIR / child).mkdir(parents=True, exist_ok=True)


async def save_submission_upload(file: UploadFile) -> tuple[str, str]:
    if file.content_type not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and image uploads are allowed.",
        )

    suffix = ALLOWED_UPLOAD_TYPES[file.content_type]
    safe_name = f"{uuid4().hex}{suffix}"
    destination_dir = settings.UPLOAD_DIR / "submissions"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / safe_name
    total_size = 0
    saw_content = False

    with destination.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            if not saw_content:
                saw_content = True
                if not _matches_declared_type(file.content_type, chunk):
                    destination.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Uploaded file content does not match its declared type.",
                    )
            total_size += len(chunk)
            if total_size > settings.max_upload_bytes:
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB.",
                )
            output.write(chunk)

    if not saw_content:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    return str(Path("uploads") / "submissions" / safe_name), file.filename or safe_name


def _matches_declared_type(content_type: str | None, chunk: bytes) -> bool:
    if content_type == "application/pdf":
        return chunk.startswith(b"%PDF")
    if content_type == "image/jpeg":
        return chunk.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return chunk.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return len(chunk) >= 12 and chunk[:4] == b"RIFF" and chunk[8:12] == b"WEBP"
    if content_type in {"image/heic", "image/heif"}:
        return len(chunk) >= 12 and chunk[4:8] == b"ftyp" and chunk[8:12] in {
            b"heic",
            b"heix",
            b"hevc",
            b"hevx",
            b"heif",
            b"mif1",
            b"msf1",
        }
    return False
