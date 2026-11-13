import logging
import os
import sys
from dotenv import load_dotenv

# MongoDB connection and error handling
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from data_manager.data_manager import DataManager
from data_manager.reportstore import ReportStore
from data_manager.mongoreportstore import MongoReportStore
from data_manager.csvreportstore import CsvReportStore
from logic_manager.moderationpipeline import ModerationPipeline
from ai_manager.providerfactory import ProviderFactory
from ai_manager.ai_manager import AIManager


def build_report_store(logger) -> ReportStore:
    """Returns a MongoReportStore if MongoDB is reachable, otherwise a CsvReportStore."""
    # 1. Read the MongoDB settings from .env
    mongo_uri = os.getenv("MONGO_URI")          # Where the MongoDB server runs
    db_name = os.getenv("MONGO_DB_NAME")        # Which database to use

    # No MongoDB settings -> fall back to CSV files in cleaned/
    if not mongo_uri or not db_name:
        logger.warning("MongoDB not configured - saving reports as CSV in cleaned/")
        return CsvReportStore()

    # 2. Settings exist, so try to connect
    # The 5-second timeout stops the app hanging for the default 30 seconds.
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    # ping the MongoDB server to check the connection works
    try:
        client.admin.command("ping")
    except PyMongoError as err:
        logger.warning("Cannot connect to MongoDB (%s) - saving reports as CSV in cleaned/", err)
        return CsvReportStore()

    # 3. Connected: use the reports collection in the chosen database
    logger.info("Connected to MongoDB database '%s'", db_name)
    return MongoReportStore(client[db_name]["reports"])


def run_console(data_manager, pipeline):
    """Text menu in the terminal (used by Docker)."""
    logging.getLogger().setLevel(logging.WARNING)   # Hide INFO logs
    from io_manager.io_manager import IOManager
    io_manager = IOManager(data_manager)
    io_manager.main_menu(process_callback=pipeline.process)


def run_gui(data_manager, pipeline):
    """PySide6 window (used when running on your own laptop)."""
    from PySide6.QtWidgets import QApplication
    from io_manager.gui_view import GUIView
    app = QApplication(sys.argv)
    window = GUIView(data_manager=data_manager, process_callback=pipeline.process)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    load_dotenv()  # Load API keys from .env
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize AI Provider
    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)

    # Pick where reports are saved: MongoDB if available, otherwise CSV
    report_store = build_report_store(logger)

    # Build the backend managers once using the chosen report store
    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    # Route execution to either Console or GUI based on arguments
    if "--console" in sys.argv:
        run_console(data_manager, pipeline)
    else:
        run_gui(data_manager, pipeline)