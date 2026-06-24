from pathlib import Path, PurePath
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {
    ".pdf": {"application/pdf"},
    ".png": {"image/png"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
    ".zip": {"application/zip", "application/x-zip-compressed", "application/octet-stream"},
}
DANGEROUS_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".com",
    ".exe",
    ".html",
    ".js",
    ".msi",
    ".php",
    ".ps1",
    ".scr",
    ".sh",
    ".vbs",
}
MAX_ZIP_ENTRIES = 200
MAX_ZIP_UNCOMPRESSED_BYTES = 100 * 1024 * 1024


def ensure_upload_directories() -> None:
    for child in ("submissions", "profile_images", "certificates", "projects"):
        (settings.UPLOAD_DIR / child).mkdir(parents=True, exist_ok=True)


async def save_submission_upload(file: UploadFile) -> tuple[str, str]:
    original_filename = _safe_original_filename(file.filename)
    suffix = Path(original_filename).suffix.lower()
    content_type = (file.content_type or "application/octet-stream").split(";")[0].lower()
    _validate_upload_type(suffix, content_type)

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
                if not _matches_declared_type(suffix, chunk):
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

    if suffix in {".txt", ".md"}:
        _validate_text_file(destination)
    if suffix == ".zip":
        _validate_zip_file(destination)

    return str(Path("uploads") / "submissions" / safe_name), original_filename


def resolve_upload_path(stored_path: str) -> Path:
    relative_path = Path(stored_path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    upload_root = settings.UPLOAD_DIR.resolve()
    if relative_path.parts and relative_path.parts[0] == settings.UPLOAD_DIR.name:
        candidate = settings.UPLOAD_DIR.joinpath(*relative_path.parts[1:]).resolve()
    else:
        candidate = (settings.UPLOAD_DIR / relative_path).resolve()

    if candidate != upload_root and upload_root not in candidate.parents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    if not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    return candidate


def _safe_original_filename(filename: str | None) -> str:
    name = PurePath(filename or "").name.strip()
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must have a filename.")
    suffix = Path(name).suffix.lower()
    if suffix in DANGEROUS_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This file type is not allowed.")
    if suffix not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allowed file types: png, jpg, jpeg, pdf, txt, md, zip.",
        )
    return name


def _validate_upload_type(suffix: str, content_type: str) -> None:
    if suffix in DANGEROUS_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This file type is not allowed.")
    allowed_types = ALLOWED_CONTENT_TYPES.get(suffix)
    if not allowed_types or content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file type does not match an allowed extension.",
        )


def _matches_declared_type(suffix: str, chunk: bytes) -> bool:
    if suffix == ".pdf":
        return chunk.startswith(b"%PDF")
    if suffix in {".jpg", ".jpeg"}:
        return chunk.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return chunk.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix == ".zip":
        return chunk.startswith(b"PK\x03\x04") or chunk.startswith(b"PK\x05\x06") or chunk.startswith(b"PK\x07\x08")
    if suffix in {".txt", ".md"}:
        return b"\x00" not in chunk
    return False


def _validate_text_file(path: Path) -> None:
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text uploads must be UTF-8.")


def _validate_zip_file(path: Path) -> None:
    try:
        with ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ZIP_ENTRIES:
                raise ValueError("Zip file contains too many files.")
            total_size = 0
            for entry in entries:
                entry_path = PurePath(entry.filename)
                if entry_path.is_absolute() or ".." in entry_path.parts:
                    raise ValueError("Zip file contains unsafe paths.")
                if Path(entry.filename).suffix.lower() in DANGEROUS_EXTENSIONS:
                    raise ValueError("Zip file contains blocked executable/script files.")
                total_size += entry.file_size
                if total_size > MAX_ZIP_UNCOMPRESSED_BYTES:
                    raise ValueError("Zip file is too large when extracted.")
    except (BadZipFile, ValueError) as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc) or "Invalid zip file.")
