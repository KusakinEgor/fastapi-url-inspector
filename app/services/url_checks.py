import httpx
import ssl
import asyncio
import socket
import time
from urllib.parse import urlparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional, Dict, Any, Tuple, Union
from pydantic import HttpUrl

class URLInspector:
    def __init__(self, timeout: float = 10.0, max_connection: int = 50):
        self.timeout = httpx.Timeout(timeout)

        limits = httpx.Limits(
            max_keepalive_connections=max_connection,
            max_connections=max_connection
        )

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=limits,
            follow_redirects=True
        )

    async def close(self):
        await self.client.aclose()
    
    async def _ensure_scheme(self, url: Union[str, HttpUrl]) -> str:
        url = str(url)
        parsed = urlparse(url)

        if not parsed.scheme:
            return "https://" + parsed.netloc + parsed.path
        elif parsed.scheme != "https":
            return "https://" + parsed.netloc + parsed.path
        
        return url
    
    async def check_status(self, url: Union[str, HttpUrl], timeout: Optional[float] = None) -> Optional[Tuple[int, Dict[str, str]]]:
        url = await self._ensure_scheme(url)

        try:
            response = await self.client.head(url)

            if response.status_code >= 400:
                async with self.client.stream("GET", url) as response:
                    headers = dict(response.headers)
                    status_code = response.status_code
                    return status_code, headers
            
            return response.status_code, dict(response.headers)
        except httpx.RequestError:
            return None
    
    async def measure_response_time(self, url: Union[str, HttpUrl]) -> Optional[float]:
        url = await self._ensure_scheme(url)
        start = time.perf_counter()

        try:
            await self.client.get(url)
            return time.perf_counter() - start
        except httpx.RequestError:
            return None
    
    def _check_ssl_sync(self, url: Union[str, HttpUrl], port: int = 443) -> Optional[Dict[str, Any]]:
        url = str(url)
        parsed = urlparse(url)
        host = parsed.hostname

        if not host:
            return None
        
        ctx = ssl.create_default_context()

        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    not_after = cert.get("notAfter")
                    expires = None
                    valid = False

                    if not_after:
                        expires = parsedate_to_datetime(not_after)
                        if expires and expires.tzinfo is None:
                            expires = expires.replace(tzinfo=timezone.utc)
                        valid = datetime.now(timezone.utc) < expires
                    
                    def pair_to_dict(pair):
                        out = {}
                        for item in pair or ():
                            for key, value in item:
                                out[key] = value
                        return out

                    return {
                        "valid": valid,
                        "expires": expires.isoformat() if expires else None,
                        "issuer": pair_to_dict(cert.get("issuer")),
                        "subject": pair_to_dict(cert.get("subject")),
                    }
        except Exception as e:
            print(f"SSL check failed for {host}:{port} → {e}")
            return None

    async def check_ssl(self, url: str, port: int = 443):
        return await asyncio.to_thread(self._check_ssl_sync, url, port)
    
    async def get_redirects(self, url: Union[str, HttpUrl], follow_redirects: bool = True) -> list[str]:
        url = str(url)
        response = await self.client.get(url, follow_redirects=follow_redirects)
        history = response.history

        redirects = [resp.url for resp in history]
        redirects.append(str(response.url))

        return redirects
