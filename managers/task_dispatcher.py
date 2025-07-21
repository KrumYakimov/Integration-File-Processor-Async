from typing import Any, Dict, List, Tuple

from services.api_clients import AgifyClient, JokeClient, PostmanClient
from utils.logger import info_logger, error_logger
from validators.input_validator import InputValidator


class AsyncTaskDispatcher:
    """Dispatches tasks to external API clients and manages caching for age predictions."""

    def __init__(self) -> None:
        """Initialize API clients and internal age cache."""
        self.age_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.agify_client = AgifyClient()
        self.joke_client = JokeClient()
        self.postman_client = PostmanClient()

    async def preload_age_predictions(
        self, name_country_pairs: List[Tuple[str, str]]
    ) -> None:
        """
        Preload and cache age predictions for batches of (name, country) pairs.

        :param name_country_pairs: List of (name, country) tuples to preload predictions for.
        """
        country_groups: Dict[str, List[str]] = {}
        for name, country in name_country_pairs:
            country = country.upper()
            country_groups.setdefault(country, []).append(name)

        for country, names in country_groups.items():
            for i in range(0, len(names), 10):
                batch = names[i : i + 10]
                try:
                    results = await self.agify_client.get_batch_ages(batch, country)
                    info_logger.info(
                        f"[BATCH] {len(batch)} names in {country}: {', '.join(batch)}"
                    )
                    for result in results:
                        self.age_cache[(result["name"], country)] = result
                except Exception as e:
                    error_logger.error(
                        f"[BATCH] Failed batch request for {country}: {str(e)}"
                    )

    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single task based on its type ("age", "joke", etc.).

        :param data: Input data dict with a "type" field.
        :return: Processed result posted through PostmanClient.
        :raises Exception: If any error occurs during processing.
        """

        task_type: str = data.get("type", "").lower()
        name: str = data.get("name", "")
        country: str = data.get("country", "").upper()

        try:
            if task_type == "age":
                key = (name, country)
                if key not in self.age_cache:
                    result = await self.agify_client.get_age(name, country)
                    info_logger.info(f"[SINGLE] Age fetched for {name} in {country}")
                    self.age_cache[key] = result
                response: Dict[str, Any] = self.age_cache[key]

            elif task_type == "joke":
                response = await self.joke_client.get_random_joke()
                info_logger.info(f"[JOKE] Random joke fetched")

            else:
                response = data
                info_logger.info(
                    f"[RAW] Unrecognized task_type. Used input as response."
                )

            postman_response = await self.postman_client.post_response(response)
            return postman_response.get("json", {})

        except Exception as e:
            error_logger.error(f"[TASK] Failed to handle task: {str(e)}")
            raise
