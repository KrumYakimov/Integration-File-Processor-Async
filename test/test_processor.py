import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from resources.processor import AsyncJsonProcessor


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.processor
@pytest.mark.parametrize(
    "task_data,expected_response",
    [
        ({"type": "age", "name": "Alice", "country": "US"}, {"age": 30}),
        ({"type": "joke"}, {"joke": "Why did the chicken cross the road?"}),
        ({"type": "unknown", "name": "X"}, {"type": "unknown", "name": "X"}),
    ],
)
async def test_process_file_types(
    tmp_path: Path, task_data: dict, expected_response: dict
) -> None:
    """
    Parametrized test for different task types (age, joke, unknown).
    """
    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(task_data), encoding="utf-8")

    mock_dispatcher = MagicMock()
    mock_dispatcher.handle = AsyncMock(return_value=expected_response)

    with patch(
        "resources.processor.AsyncFileManager.read_json", return_value=task_data
    ), patch(
        "resources.processor.AsyncFileManager.write_json", new_callable=AsyncMock
    ) as mock_write, patch(
        "resources.processor.AsyncFileManager.delete_file", new_callable=AsyncMock
    ) as mock_delete:

        processor = AsyncJsonProcessor()
        await processor.process_file(mock_dispatcher, test_file)

        output_file = test_file.with_name(f"{test_file.stem}_processed.json")

        mock_dispatcher.handle.assert_awaited_once_with(task_data)
        mock_write.assert_awaited_once_with(output_file, expected_response)
        mock_delete.assert_awaited_once_with(test_file)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.processor
async def test_process_file_with_unexpected_task_type(tmp_path: Path) -> None:
    """
    Test that an unrecognized task type is still processed by returning the raw input.
    """
    test_data = {"type": "foo", "name": "John", "country": "BG"}
    test_file = tmp_path / "unexpected.json"
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    mock_dispatcher = MagicMock()
    mock_dispatcher.handle = AsyncMock(return_value=test_data)

    with patch(
        "resources.processor.AsyncFileManager.read_json", return_value=test_data
    ), patch(
        "resources.processor.AsyncFileManager.write_json", new_callable=AsyncMock
    ) as mock_write, patch(
        "resources.processor.AsyncFileManager.delete_file", new_callable=AsyncMock
    ) as mock_delete:

        processor = AsyncJsonProcessor()
        await processor.process_file(mock_dispatcher, test_file)

        output_file = test_file.with_name("unexpected_processed.json")

        mock_dispatcher.handle.assert_awaited_once_with(test_data)
        mock_write.assert_awaited_once_with(output_file, test_data)
        mock_delete.assert_awaited_once_with(test_file)
