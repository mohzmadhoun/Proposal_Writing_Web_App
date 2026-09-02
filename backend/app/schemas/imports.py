from pydantic import BaseModel


class MarkdownImportRequest(BaseModel):
    directory_path: str


class MarkdownImportResponse(BaseModel):
    scanned_files: int
    created_records: int
    updated_records: int
    skipped_records: int
    messages: list[str]
