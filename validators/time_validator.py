import re


def validate_process_time(time_str: str) -> bool:
    """
    Validate whether the provided string matches the HH:MM 24-hour time format.

    Accepted formats:
    - "00:00" through "23:59"
    - Leading zeros are required (e.g., "09:30" is valid, "9:30" is not)

    :param time_str: A string representing time in HH:MM format.
    :return: True if the time is valid, False otherwise.
    """
    return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_str))
