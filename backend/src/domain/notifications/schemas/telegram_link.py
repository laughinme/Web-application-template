from pydantic import BaseModel


class TelegramConnectLinkResponse(BaseModel):
    url: str
    expires_in: int
