import asyncio
import json
from typing import Any, Self
from urllib.parse import quote

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import Settings
from app.service.ports import ObjectInfo

_MISSING_CODES = {"404", "NoSuchKey", "NotFound"}


class ObjectStorage:
    """
    S3-compatible storage. boto3 is blocking, so every network call goes to a thread;
    callers only see async methods.
    """

    def __init__(
        self,
        *,
        internal_endpoint: str,
        public_endpoint: str,
        region: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        use_path_style: bool,
    ) -> None:
        config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if use_path_style else "auto"},
        )
        credentials: dict[str, Any] = {
            "region_name": region,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "config": config,
        }
        self._client = boto3.client("s3", endpoint_url=internal_endpoint, **credentials)
        # Presigned URLs are signed for the host the browser will call.
        self._presigner = boto3.client("s3", endpoint_url=public_endpoint, **credentials)
        self._public_endpoint = public_endpoint
        self._region = region
        self.bucket = bucket

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        return cls(
            internal_endpoint=settings.storage_endpoint_internal,
            public_endpoint=settings.storage_endpoint_public,
            region=settings.storage_region,
            access_key=settings.storage_access_key,
            secret_key=settings.storage_secret_key.get_secret_value(),
            bucket=settings.storage_public_bucket,
            use_path_style=settings.storage_use_path_style,
        )

    def public_url(self, key: str) -> str:
        return f"{self._public_endpoint}/{self.bucket}/{quote(key, safe='/')}"

    def presign_upload(self, key: str, *, content_type: str, expires_in: int) -> str:
        url: str = self._presigner.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        return url

    async def stat(self, key: str) -> ObjectInfo | None:
        try:
            head = await asyncio.to_thread(self._client.head_object, Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if str(exc.response.get("Error", {}).get("Code")) in _MISSING_CODES:
                return None
            raise
        return ObjectInfo(
            size_bytes=int(head.get("ContentLength", 0)),
            content_type=head.get("ContentType"),
        )

    async def put(self, key: str, data: bytes, *, content_type: str) -> None:
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    async def delete(self, key: str) -> None:
        # S3 delete is idempotent: deleting a missing key is not an error.
        await asyncio.to_thread(self._client.delete_object, Bucket=self.bucket, Key=key)

    async def ping(self) -> None:
        await asyncio.to_thread(self._client.head_bucket, Bucket=self.bucket)

    async def ensure_bucket(self) -> None:
        """Dev/test convenience: create the bucket and make its objects publicly readable."""
        try:
            await self.ping()
        except ClientError:
            kwargs: dict[str, Any] = {"Bucket": self.bucket}
            if self._region != "us-east-1":
                kwargs["CreateBucketConfiguration"] = {"LocationConstraint": self._region}
            await asyncio.to_thread(self._client.create_bucket, **kwargs)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                }
            ],
        }
        await asyncio.to_thread(
            self._client.put_bucket_policy, Bucket=self.bucket, Policy=json.dumps(policy)
        )
