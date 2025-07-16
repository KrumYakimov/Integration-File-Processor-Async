import json
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os


class AsyncFileManager:
    @staticmethod
    async def get_json_files(input_path: Path) -> list[Path]:
        """
        Recursively retrieves all JSON files located in nested subdirectories of the input path.

        Note:
            The input directory may contain multiple folders with arbitrary names
            (e.g. per day), and JSON files are expected to be inside those folders.

        :param input_path: The INPUT directory path where folders are placed.
        :return: List of Path objects pointing to JSON files.
        """
        return list(input_path.rglob("*.json"))

    @staticmethod
    async def read_json(path: Path) -> dict[str, Any]:
        """
        Asynchronously reads and parses a JSON file.

        :param path: The path to the JSON file.
        :return: The file content as a dictionary.
        """
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)

    @staticmethod
    async def write_json(path: Path, data: dict[str, Any]) -> None:
        """
        Asynchronously writes a dictionary to a file in JSON format.

        :param path: The file path to write to.
        :param data: The dictionary to serialize and write.
        """
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    @staticmethod
    async def delete_file(path: Path) -> None:
        """
        Asynchronously deletes a file from the filesystem.

        :param path: The path of the file to delete.
        """
        await aiofiles.os.remove(path)
