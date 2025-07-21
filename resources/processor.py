import asyncio
import time
from pathlib import Path
from typing import List, Tuple

from managers.file_manager import AsyncFileManager
from managers.task_dispatcher import AsyncTaskDispatcher
from utils.logger import info_logger, error_logger
from validators.input_validator import InputValidator


class AsyncJsonProcessor:
    """
    Asynchronous processor for reading, handling, and writing JSON files.
    Handles input from a directory, preloads data (e.g. age predictions),
    and dispatches processing tasks.
    """

    PROCESSED_SUFFIX = "_processed"

    def __init__(self, input_path: Path = Path("INPUT")):
        self.input_path = input_path

    @staticmethod
    async def read_and_validate(file: Path) -> dict:
        """
        Reads a JSON file and validates its content.

        :param file: Path to the input file.
        :return: Parsed and validated JSON data.
        :raises: Exception if the file is invalid or unreadable.
        """
        data: dict = await AsyncFileManager.read_json(file)
        InputValidator.validate(data)
        return data

    async def process_file(
        self, dispatcher: AsyncTaskDispatcher, file: Path, content: dict
    ) -> None:
        """
        Process a single JSON file that has already been validated:
        - Passes the content to the dispatcher for further processing.
        - Writes the processed result to a new file with a "_processed" suffix.
        - Deletes the original input file upon successful processing.
        - Logs the duration and success/failure of the processing.

        :param dispatcher: Dispatcher instance used to process content.
        :param file: Path to the input JSON file. Used for naming the output file and deletion.
        :param content: The already validated dictionary content of the JSON file.
        """
        start_time = time.time()
        info_logger.info(f"{file.name} – processing started.")

        try:
            response: dict = await dispatcher.handle(content)

            output_path: Path = file.with_name(
                f"{file.stem}{self.PROCESSED_SUFFIX}.json"
            )
            await AsyncFileManager.write_json(output_path, response)
            await AsyncFileManager.delete_file(file)

            duration: float = round(time.time() - start_time, 2)
            info_logger.info(
                f"{file.name} – processed successfully in {duration} seconds. Status: SUCCESS"
            )

        except Exception as e:
            duration: float = round(time.time() - start_time, 2)
            error_logger.error(
                f"{file.name} – failed after {duration} seconds. Reason: {str(e)}"
            )

    async def process_all(self) -> None:
        """
        Process all JSON files in the input directory:
        - Collects all `.json` files.
        - Validates each file's content early in the process. Invalid or unreadable files are skipped and logged.
        - Preloads age prediction requests if type is "age".
        - Calls the dispatcher to handle the rest of the content.
        - Runs all processing tasks concurrently.
        """
        files: List[Path] = await AsyncFileManager.get_json_files(self.input_path)
        valid_data_map: List[Tuple[Path, dict]] = []

        for file in files:
            try:
                data = await self.read_and_validate(file)
                valid_data_map.append((file, data))
            except Exception as e:
                error_logger.error(f"{file.name} – skipped. Reason: {str(e)}")

        age_inputs: List[Tuple[str, str]] = [
            (data["name"], data["country"].upper())
            for _, data in valid_data_map
            if data.get("type", "").lower() == "age"
        ]

        unique_inputs: List[Tuple[str, str]] = list(set(age_inputs))
        info_logger.info(
            f"Preloading {len(unique_inputs)} unique (name, country) pairs..."
        )

        dispatcher = AsyncTaskDispatcher()
        await dispatcher.preload_age_predictions(unique_inputs)

        info_logger.info(f"Processing {len(valid_data_map)} files...")

        tasks = [
            self.process_file(dispatcher, file, data) for file, data in valid_data_map
        ]
        await asyncio.gather(*tasks)
