import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import main


@pytest.mark.integration
@pytest.mark.main
def test_main_processes_json_file(tmp_path: Path) -> None:
    """
    Integration test for main() that processes real JSON file using mock API client.
    """
    input_dir = tmp_path / "INPUT"
    input_dir.mkdir()

    test_file = input_dir / "test.json"
    test_data = {"type": "joke", "name": "John", "country": "US"}
    expected_response = {"joke": "Mocked joke"}

    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    with patch(
        "resources.processor.AsyncTaskDispatcher.handle", new_callable=AsyncMock
    ) as mock_handle:
        mock_handle.return_value = expected_response

        main.main(input_dir)  # calls asyncio.run(processor.process_all())

        processed_file = input_dir / "test_processed.json"
        assert not test_file.exists(), "Input file should be deleted"
        assert processed_file.exists(), "Processed file should be created"

        with processed_file.open(encoding="utf-8") as f:
            result = json.load(f)

        assert result == expected_response
