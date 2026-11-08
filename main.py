import logging
import os
import sys
from dotenv import load_dotenv
# for mongoDB connection and error handling
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from PySide6.QtWidgets import QApplication
from data_manager import DataManager
from moderationpipeline import ModerationPipeline
from providerfactory import ProviderFactory
from mongoreportstore import MongoReportStore
#from csvreportstore import CsvReportStore
from ai_manager import AIManager
# Import the GUI View
from gui_view import GUIView

if __name__ == "__main__":
    load_dotenv()  # Load API keys from .env
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)

    # 1. Read the MongoDB settings from .env (loaded above by load_dotenv)
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

    # show on startup if succesfully connected to MongoDB
    logger.info("Connected to MongoDB database '%s'", db_name)

    # Access the specified database and the reports collection within it
    report_store = MongoReportStore(client[db_name]["reports"])

    # Documents stored in the reports collection are passed to the data manager 
    data_manager = DataManager(report_store)

    # 3. Initialize the moderation pipeline
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    # 4. Start the PySide6 Application Loop
    app = QApplication(sys.argv)
    
    # 5. Create the GUI Window, passing the backend dependencies
    window = GUIView(data_manager=data_manager, process_callback=pipeline.process)
    window.show()
    
    # 6. Safely execute the application and exit when closed
    sys.exit(app.exec())