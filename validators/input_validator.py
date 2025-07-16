import re
from typing import Any


class InputValidator:
    """Validator for input JSON data related to task dispatching."""

    @staticmethod
    def validate(json_data: dict[str, Any]) -> None:
        """
        Validate the structure and content of a given JSON dictionary.

        This method checks for the presence and format of the 'name', 'type',
        and 'country' fields in the input data. If any validations fail, it
        raises a ValueError with all relevant error messages.

        :param json_data: Dictionary representing the input JSON data.
        :raises ValueError: If the input data is not valid.
        """
        errors: list[str] = []

        if not isinstance(json_data, dict):
            raise ValueError("Input data must be a JSON object.")

        name = json_data.get("name")
        if not name or not isinstance(name, str):
            errors.append("Missing or invalid 'name' field.")
        elif len(name) < 2 or len(name) > 64:
            errors.append("Invalid 'name': must be between 2 and 64 characters.")
        elif not re.fullmatch(r"[A-Za-zÀ-ÿ\s\-]+", name):
            errors.append(f"Invalid 'name': '{name}' contains invalid characters.")

        task_type = json_data.get("type")
        if not task_type or not isinstance(task_type, str):
            errors.append("Missing or invalid 'type' field.")
        elif len(task_type) < 2 or len(task_type) > 32:
            errors.append("Invalid 'type': must be between 2 and 32 characters.")
        elif not re.fullmatch(r"[a-zA-Z_]+", task_type):
            errors.append(f"Invalid 'type': '{task_type}' contains invalid characters.")

        country = json_data.get("country")
        if not country or not isinstance(country, str):
            errors.append("Missing or invalid 'country' field.")
        elif not re.fullmatch(r"[A-Z]{2}", country.upper()):
            errors.append(
                f"Invalid country code '{country}'. Must be ISO 3166-1 alpha-2."
            )

        if errors:
            raise ValueError("; ".join(errors))
