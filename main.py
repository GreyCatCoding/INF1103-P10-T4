import logging
import sys

from dotenv import load_dotenv

from io_manager import IOManager
from ai_manager import AIManager
from data_manager import DataManager
from moderationpipeline import ModerationPipeline
from providerfactory import ProviderFactory
from csvreportstore import CsvReportStore

if __name__ == "__main__":
    load_dotenv()  # Load API keys from .env
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)


    report_store = CsvReportStore()
    data_manager = DataManager(report_store)

    pipeline = ModerationPipeline(AIManager(provider), data_manager)
    io_manager = IOManager(data_manager)

    io_manager.main_menu(process_callback=pipeline.process)