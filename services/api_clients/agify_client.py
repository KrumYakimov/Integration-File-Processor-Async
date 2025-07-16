from typing import Any, Union

from services.api_clients.base_client import BaseAPIClient


class AgifyClient(BaseAPIClient):
    """Client for interacting with the Agify API."""

    BASE_URL: str = "https://api.agify.io"

    async def get_age(self, name: str, country: str) -> dict[str, Any]:
        """
        Get age prediction for a single name.

        :param name: Person's name.
        :param country: Country code (ISO 3166-1 alpha-2).
        :return: API response containing age prediction.
        """
        params = {"name": name, "country_id": country}
        return await self.get(self.BASE_URL, params=params)

    async def get_batch_ages(
        self, names: list[str], country: str
    ) -> Union[list[dict[str, Any]], dict[str, Any]]:
        """
        Get age predictions for a batch of names (max 10).

        :param names: List of names (up to 10).
        :param country: Country code.
        :return: List of API responses for each name.
        :raises ValueError: If more than 10 names are passed.
        """
        if not names:
            return []

        if len(names) > 10:
            raise ValueError("Agify API supports up to 10 names per batch request.")

        params = [("name[]", name) for name in names]
        params.append(("country_id", country))

        return await self.get(self.BASE_URL, params=params)
