import asyncio
from pathlib import Path

from resources.processor import AsyncJsonProcessor


def main(input_dir: Path = Path("INPUT")):
    processor = AsyncJsonProcessor(input_dir)
    asyncio.run(processor.process_all())


if __name__ == "__main__":
    main()
