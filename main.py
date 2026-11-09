import logging
import os
import sys
from dotenv import load_dotenv

# MongoDB connection and error handling
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from data_manager import DataManager
from moderationpipeline import ModerationPipeline
from providerfactory import ProviderFactory
from mongoreportstore import MongoReportStore
from ai_manager import AIManager


def run_console(data_manager, pipeline):
    """Text menu in the terminal (used by Docker)."""
    logging.getLogger().setLevel(logging.WARNING)   # Hide INFO logs
    from io_manager import IOManager
    io_manager = IOManager(data_manager)
    io_manager.main_menu(process_callback=pipeline.process)


def run_gui(data_manager, pipeline):
    """PySide6 window (used when running on your own laptop)."""
    from PySide6.QtWidgets import QApplication
    from gui_view import GUIView
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

    # 1. Read the MongoDB settings from .env
    mongo_uri = os.getenv("MONGO_URI")          # Where the MongoDB server runs
    db_name = os.getenv("MONGO_DB_NAME")        # Which database to use

    # Stop early with a clear message if either setting is missing
    if not mongo_uri or not db_name:
        logger.error("Cannot start: MONGO_URI and MONGO_DB_NAME must be set in .env")
        sys.exit(1)

    # 2. Connect to MongoDB and stop early if it is unreachable
    # The 5-second timeout stops the app hanging for the default 30 seconds.
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    # ping the MongoDB server to ensure the connection is valid
    try:
        client.admin.command("ping")
    except PyMongoError as err:
        logger.error("Cannot connect to MongoDB: %s", err)
        sys.exit(1)

    # show on startup if successfully connected to MongoDB
    logger.info("Connected to MongoDB database '%s'", db_name)

    # Access the specified database and the reports collection within it
    report_store = MongoReportStore(client[db_name]["reports"])

    # 3. Build the backend managers once using the MongoReportStore
    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    # 4. Route execution to either Console or GUI based on arguments
    if "--console" in sys.argv:
        run_console(data_manager, pipeline)
    else:
        run_gui(data_manager, pipeline)