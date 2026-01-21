from pydantic import BaseModel


class UserMessage(BaseModel):
    content: str
    thread_id: str


class UploadResponse(BaseModel):
    filename: str
    chunks_generated: int
    status: str
