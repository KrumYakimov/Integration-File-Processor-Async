import asyncio
import time

import schedule

from config.settings import PROCESS_TIME
from resources.processor import AsyncJsonProcessor
from utils.logger import info_logger
from validators.time_validator import validate_process_time


async def job():
    info_logger.info("Starting daily async processing...")
    processor = AsyncJsonProcessor()
    await processor.process_all()


def run_scheduler() -> None:
    if not validate_process_time(PROCESS_TIME):
        raise ValueError(
            f"Invalid PROCESS_TIME format: '{PROCESS_TIME}'. Expected HH:MM."
        )

    def sync_wrapper():
        asyncio.run(job())

    schedule.every().day.at(PROCESS_TIME).do(sync_wrapper)
    info_logger.info(f"Scheduler started. Waiting for scheduled time: {PROCESS_TIME}")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
