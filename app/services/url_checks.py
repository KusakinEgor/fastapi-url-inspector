import httpx
import ssl
import asyncio
import socket
import time
from urllib.parse import urlparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional, Dict, Any

class URLInspector:
    def __init__(self, timeout: float = 10.0, max_connection: int = 100):
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
    
    async def _ensure_scheme(self, url: str) -> str:
        parsed = urlparse(url)

        if not parsed.scheme:
            return "http://" + url
        
        return url
    
    async def check_status(self, url: str, timeout: Optional[float] = None) -> Optional[int]:
        url = await self._ensure_scheme(url)

        try:
            response = await self.client.head(url)

            if response.status_code >= 400:
                response = await self.client.get(url, stream=True)
            
            return dict(response.headers)
        except httpx.RequestError:
            return None
    
    async def measure_response_time(self, url: str) -> Optional[float]:
        url = await self._ensure_scheme(url)
        start = time.perf_counter()

        try:
            response = await self.client.get(url)
            return time.perf_counter() - start
        except httpx.RequestError:
            return None
    
    async def check_ssl(self, url: str, port: int = 433) -> Optional[Dict[str, Any]]:
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.path

        if not hostname:
            return None
        
        def _get_cert():
            ctx = ssl.create_default_context()

            with socket.create_connection((hostname, port), timeout=5) as socket:
                with ctx.wrap_socket(socket, server_hostname=hostname) as wrap_socket:
                    cert = wrap_socket.getpeercert()
            not_after = cert.get("notAfter")
            expires = None

            if not_after:
                try:
                    expires = parsedate_to_datetime(not_after)
                except Exception:
                    expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            
            def pair_to_dict(pair):
                out = {}

                for item in pair or ():
                    for key, value in item:
                        out[key] = value
                return out
        
            issuer = pair_to_dict(cert.get("issuer"))
            subject = pair_to_dict(cert.get("subject"))
            valid = None

            if expires:
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                valid = datetime.now(timezone.utc) < expires
            
            return {
                "valid": valid,
                "expires": expires.isoformat() if expires is not None else None,
                "issuer": issuer,
                "subject": subject,
            }
        
        try:
            return await asyncio.to_thread(_get_cert)
        except Exception:
            return None
