from typing import Any

from services.api_clients.base_client import BaseAPIClient


class PostmanClient(BaseAPIClient):
    """Client for testing HTTP POST requests using Postman Echo."""

    BASE_URL: str = "https://postman-echo.com/post"

    async def post_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Send a POST request and get the echoed response.

        :param data: Dictionary to send in the request body.
        :return: Echoed response from Postman Echo.
        """
        return await self.post(self.BASE_URL, data)
