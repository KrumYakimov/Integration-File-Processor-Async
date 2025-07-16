import json
from pathlib import Path

import pytest

from managers.file_manager import AsyncFileManager

pytestmark = pytest.mark.asyncio


@pytest.mark.unit
@pytest.mark.fileio
@pytest.mark.parametrize(
    "test_data",
    [
        {"type": "age", "name": "Alice", "country": "US"},
        {"type": "joke", "name": "Bob", "country": "DE"},
        {"type": "age", "name": "Émilie", "country": "FR"},
        {"type": "age", "name": "李雷", "country": "CN"},
    ],
)
async def test_write_and_read_json(tmp_path: Path, test_data: dict):
    """
    Test writing JSON to a file and reading it back.
    """
    test_file = tmp_path / "test.json"

    await AsyncFileManager.write_json(test_file, test_data)
    assert test_file.exists()

    data = await AsyncFileManager.read_json(test_file)
    assert data == test_data


@pytest.mark.unit
@pytest.mark.fileio
async def test_delete_file(tmp_path: Path):
    """
    Test deleting a file from disk.
    """
    test_file = tmp_path / "delete_me.json"
    test_file.write_text(json.dumps({"key": "value"}), encoding="utf-8")
    assert test_file.exists()

    await AsyncFileManager.delete_file(test_file)
    assert not test_file.exists()


@pytest.mark.unit
@pytest.mark.fileio
async def test_get_json_files(tmp_path: Path):
    """
    Test recursively finding all .json files in a directory.
    """
    nested_dir = tmp_path / "subdir"
    nested_dir.mkdir()
    (tmp_path / "file1.json").write_text("{}", encoding="utf-8")
    (nested_dir / "file2.json").write_text("{}", encoding="utf-8")
    (tmp_path / "not_json.txt").write_text("Not JSON", encoding="utf-8")

    json_files = await AsyncFileManager.get_json_files(tmp_path)
    json_file_names = sorted(f.name for f in json_files)

    assert "file1.json" in json_file_names
    assert "file2.json" in json_file_names
    assert "not_json.txt" not in json_file_names