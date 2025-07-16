from typing import Any, Optional

import httpx


class BaseAPIClient:
    """Base asynchronous HTTP client using httpx for GET and POST requests."""

    TIMEOUT: int = 5  # seconds

    async def get(
        self, url: str, params: Optional[dict | list[tuple[str, Any]]] = None
    ) -> dict:
        """
        Send an asynchronous GET request.

        :param url: The target URL.
        :param params: Optional query parameters as a dictionary or list of tuples.
        :return: Parsed JSON response as a dictionary.
        :raises httpx.HTTPStatusError: If the response contains an error status.
        """
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, url: str, data: Optional[dict] = None) -> dict:
        """
        Send an asynchronous POST request.

        :param url: The target URL.
        :param data: Optional payload as a dictionary.
        :return: Parsed JSON response as a dictionary.
        :raises httpx.HTTPStatusError: If the response contains an error status.
        """
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
