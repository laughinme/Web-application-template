import jwt
import secrets
import hmac

from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

from core.config import Settings
from database.redis import CacheRepo

config = Settings() # pyright: ignore[reportCallIssue]
PRIVATE_KEY = config.JWT_PRIVATE_KEY.encode()
PUBLIC_KEY = config.JWT_PUBLIC_KEY.encode()


class TokenService:
    def __init__(self, repo: CacheRepo):
        self.repo = repo
        
    async def issue_tokens(
        self, 
        user_id: UUID | str, 
        src: Literal['web', 'mobile'] = 'web'
    ) -> tuple[str, str, str]:
        user_id = str(user_id)
        now = datetime.now(timezone.utc)
        
        access_payload = {
            'sub': user_id,
            'src': src,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=config.ACCESS_TTL)).timestamp()),
        }
        access = jwt.encode(access_payload, PRIVATE_KEY, algorithm=config.JWT_ALGO)

        jti = uuid4().hex
        refresh_payload = {
            'sub': user_id,
            'jti': jti,
            'src': src,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=config.REFRESH_TTL)).timestamp()),
        }
        refresh = jwt.encode(refresh_payload, PRIVATE_KEY, algorithm=config.JWT_ALGO)
        await self.repo.set(f'refresh:{jti}', user_id, config.REFRESH_TTL)
        
        csrf = secrets.token_urlsafe(32)
        await self.repo.set(f'csrf:{jti}', csrf, config.REFRESH_TTL)
        
        return access, refresh, csrf


    async def refresh_tokens(self, refresh_token: str, csrf: str | None = None) -> tuple[str, str, str] | None:
        try:
            payload = jwt.decode(refresh_token, PUBLIC_KEY, algorithms=[config.JWT_ALGO])
        except jwt.PyJWTError:
            return None
        
        jti = payload.get('jti')
        
        await self.repo.delete(f'refresh:{jti}')
        
        user_id = payload['sub']
        src = payload['src']
        
        if src == 'web':
            stored_csrf = await self.repo.get(f'csrf:{jti}')
            if stored_csrf is None or csrf is None: return
        
            if not hmac.compare_digest(stored_csrf, csrf):
                return
        
        await self.repo.delete(f'csrf:{jti}')
        
        return await self.issue_tokens(user_id, src)
        
        
    async def revoke(self, refresh_token: str) -> None:
        try:
            payload = jwt.decode(refresh_token, PUBLIC_KEY, algorithms=[config.JWT_ALGO])
            jti = payload.get('jti')
            
            await self.repo.delete(f'refresh:{jti}')
            await self.repo.delete(f'csrf:{jti}')
            
        except jwt.PyJWTError:
            return None

    def verify_access(self, token: str) -> dict[str, str] | None:
        try: 
            return jwt.decode(token, PUBLIC_KEY, algorithms=[config.JWT_ALGO])
        except jwt.PyJWTError:
            return
