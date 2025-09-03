import httpx
import ssl
import asyncio
import socket
from urllib.parse import urlparse
from datetime import datetime

async def check_status(url: str, timeout: int = 5) -> int:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        return response.status_code

async def check_ssl(url: str) -> dict:
    def _get_cert():
        parsed = urlparse(url)
        hostname = parsed.hostname

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        
        not_after = cert.get("notAfter")
        expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")

        return {
            "valid": datetime.utcnow() < expires,
            "expires": expires.isoformat(),
            "issuer": dict(x[0] for x in cert.get("issuer")),
            "subject": dict(x[0] for x in cert.get("subject")),
        }
    
    return await asyncio.to_thread(_get_cert)

async def fetch_headers(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.head(url)
        return dict(response.headers)

async def measure_response_time(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.elapsed.total_seconds()

async def extract_meta(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return {"title": "Example", "description": "Stub"}
