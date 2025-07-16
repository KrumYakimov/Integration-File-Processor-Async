from typing import Any

from services.api_clients.base_client import BaseAPIClient


class JokeClient(BaseAPIClient):
    """Client for retrieving random jokes."""

    BASE_URL: str = "https://official-joke-api.appspot.com/random_joke"

    async def get_random_joke(self) -> dict[str, Any]:
        """
        Retrieve a random joke.

        :return: Dictionary containing joke data.
        """
        return await self.get(self.BASE_URL)
