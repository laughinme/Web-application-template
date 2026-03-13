from datetime import datetime

from pydantic import BaseModel, Field


class UserNotificationSettings(BaseModel):
    email_enabled: bool = Field(..., description="Enable e-mail notifications")
    telegram_enabled: bool = Field(..., description="Enable Telegram notifications")
    telegram_linked: bool = Field(..., description="Telegram account is linked")
    telegram_username: str | None = Field(None, description="Telegram username")


class UserNotificationSettingsPatch(BaseModel):
    email_enabled: bool | None = Field(None, description="Enable e-mail notifications")
    telegram_enabled: bool | None = Field(None, description="Enable Telegram notifications")


class TelegramDeeplinkResponse(BaseModel):
    deeplink_url: str = Field(..., description="Open this URL to link Telegram account")
    expires_at: datetime = Field(..., description="UTC expiration timestamp")


class TelegramLinkRequest(BaseModel):
    token: str = Field(..., min_length=8, max_length=64)
    chat_id: str = Field(..., min_length=1, max_length=64)
    username: str | None = Field(None, max_length=255)
