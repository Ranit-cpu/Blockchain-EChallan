import asyncio
from typing import Any
import aiofiles
import httpx
from app.config import settings
from app.core.exceptions import IPFSError
from app.core.logging import get_logger

logger = get_logger(__name__)


class IPFSClient:
    _instance: "IPFSClient | None" = None

    def __init__(self) -> None:
        self.base_url = f"{settings.IPFS_PROTOCOL}://{settings.IPFS_HOST}:{settings.IPFS_PORT}/api/v0"
        self.timeout = settings.IPFS_TIMEOUT
        self.max_file_size = settings.max_file_size_bytes

    @classmethod
    def get_instance(cls) -> "IPFSClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def add_bytes(self, data: bytes, filename: str = "file") -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/add",
                    files={"file": (filename, data)},
                    params={"pin": "true", "cid-version": "1"},
                )
                response.raise_for_status()
                result = response.json()
                cid = result["Hash"]
                logger.info("File added to IPFS", cid=cid, filename=filename)
                return {
                    "cid": cid,
                    "size": result.get("Size", len(data)),
                    "url": self.get_gateway_url(cid),
                }
        except httpx.HTTPError as e:
            logger.error("IPFS add failed", error=str(e))
            raise IPFSError(f"Failed to add file to IPFS: {e}")
        except Exception as e:
            logger.error("IPFS unexpected error", error=str(e))
            raise IPFSError(f"IPFS error: {e}")

    async def add_file(self, file_path: str, filename: str | None = None) -> dict[str, Any]:
        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()
        return await self.add_bytes(data, filename or file_path.split("/")[-1])

    async def cat(self, cid: str) -> bytes:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cat",
                    params={"arg": cid},
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            raise IPFSError(f"Failed to retrieve file from IPFS: {e}")

    async def pin(self, cid: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/pin/add",
                    params={"arg": cid},
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning("IPFS pin failed", cid=cid, error=str(e))
            return False

    def get_gateway_url(self, cid: str) -> str:
        return f"{settings.IPFS_PROTOCOL}://{settings.IPFS_HOST}:8080/ipfs/{cid}"

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(f"{self.base_url}/id")
                return response.status_code == 200
        except Exception:
            return False


def get_ipfs_client() -> IPFSClient:
    return IPFSClient.get_instance()