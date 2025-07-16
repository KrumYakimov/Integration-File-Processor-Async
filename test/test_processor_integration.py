import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from resources.processor import AsyncJsonProcessor


@pytest.mark.asyncio
@pytest.mark.integration
async def test_processor_integration_creates_output_and_deletes_input(tmp_path: Path) -> None:
    """
    Integration test: processes a real JSON file using a mocked dispatcher and checks
    that output file is created and input file is deleted.
    """
    input_data = {"type": "age", "name": "Alice", "country": "US"}
    input_file = tmp_path / "test_input.json"
    input_file.write_text(json.dumps(input_data), encoding="utf-8")

    expected_output = {"age": 42}
    mock_dispatcher = MagicMock()
    mock_dispatcher.handle = AsyncMock(return_value=expected_output)

    processor = AsyncJsonProcessor()
    await processor.process_file(mock_dispatcher, input_file)

    output_file = tmp_path / "test_input_processed.json"
    assert not input_file.exists()
    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as f:
        output_data = json.load(f)

    assert output_data == expected_output


@pytest.mark.asyncio
@pytest.mark.integration
async def test_processor_integration_handles_joke_task(tmp_path: Path) -> None:
    """
    Integration test: processes a 'joke' task using real file ops and a mocked dispatcher.
    """
    input_data = {"type": "joke"}
    input_file = tmp_path / "joke_input.json"
    input_file.write_text(json.dumps(input_data), encoding="utf-8")

    expected_output = {"joke": "Why did the developer go broke? Because he used up all his cache!"}
    mock_dispatcher = MagicMock()
    mock_dispatcher.handle = AsyncMock(return_value=expected_output)

    processor = AsyncJsonProcessor()
    await processor.process_file(mock_dispatcher, input_file)

    output_file = tmp_path / "joke_input_processed.json"
    assert not input_file.exists()
    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as f:
        output_data = json.load(f)

    assert output_data == expected_output


@pytest.mark.asyncio
@pytest.mark.integration
async def test_processor_integration_handles_unknown_task_type(tmp_path: Path) -> None:
    """
    Integration test: processes unknown task types and writes the unchanged data to output.
    """
    input_data = {"type": "foobar", "data": "unchanged"}
    input_file = tmp_path / "unknown_task.json"
    input_file.write_text(json.dumps(input_data), encoding="utf-8")

    mock_dispatcher = MagicMock()
    mock_dispatcher.handle = AsyncMock(return_value=input_data)

    processor = AsyncJsonProcessor()
    await processor.process_file(mock_dispatcher, input_file)

    output_file = tmp_path / "unknown_task_processed.json"
    assert not input_file.exists()
    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as f:
        output_data = json.load(f)

    assert output_data == input_data
