import asyncio
import time
from pathlib import Path
from typing import List, Tuple

from config.settings import INPUT_DIR
from managers.file_manager import AsyncFileManager
from services.task_dispatcher import AsyncTaskDispatcher
from utils.logger import info_logger, error_logger


class AsyncJsonProcessor:
    """
    Asynchronous processor for reading, handling, and writing JSON files.
    Handles input from a directory, preloads data (e.g. age predictions),
    and dispatches processing tasks.
    """

    def __init__(self, input_path: Path = Path("INPUT")):
        self.input_path = input_path

    PROCESSED_SUFFIX = "_processed"

    async def process_file(self, dispatcher: AsyncTaskDispatcher, file: Path) -> None:
        """
        Process a single JSON file:
        - Reads the file.
        - Passes the content to the dispatcher.
        - Writes the processed result to a new file.
        - Deletes the original file.
        - Logs the duration and success/failure.

        :param dispatcher: Dispatcher instance used to process content.
        :param file: Path to the input JSON file.
        """
        start_time = time.time()
        info_logger.info(f"{file.name} – processing started.")

        try:
            content: dict = await AsyncFileManager.read_json(file)
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
        - Preloads age prediction requests if type is "age".
        - Calls the dispatcher to handle the rest of the content.
        - Runs all processing tasks concurrently.
        """
        files: List[Path] = await AsyncFileManager.get_json_files(self.input_path)
        age_inputs: List[Tuple[str, str]] = []

        for file in files:
            try:
                data: dict = await AsyncFileManager.read_json(file)
                if data.get("type", "").lower() == "age":
                    name = data.get("name")
                    country = data.get("country")
                    age_inputs.append((name, country))
            except Exception as e:
                error_logger.error(
                    f"{file.name} – skipped during preload. Reason: {str(e)}"
                )

        unique_inputs: List[Tuple[str, str]] = list(set(age_inputs))
        info_logger.info(
            f"Preloading {len(unique_inputs)} unique (name, country) pairs..."
        )

        dispatcher = AsyncTaskDispatcher()
        await dispatcher.preload_age_predictions(unique_inputs)

        info_logger.info(f"Processing {len(files)} files...")

        tasks = [self.process_file(dispatcher, file) for file in files]
        await asyncio.gather(*tasks)
