from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    url: str | None = None


class ScrapeResponse(BaseModel):
    status: str
    message: str
    chunks_added: int | None = None
    source: str | None = None
