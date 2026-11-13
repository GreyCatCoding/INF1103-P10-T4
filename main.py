import logging
import os
import sys
from dotenv import load_dotenv
import streamlit as st

# MongoDB connection and error handling
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from data_manager.data_manager import DataManager
from data_manager.csvreportstore import CsvReportStore
from data_manager.mongoreportstore import MongoReportStore
from logic_manager.moderationpipeline import ModerationPipeline
from ai_manager.providerfactory import ProviderFactory
from ai_manager.ai_manager import AIManager

# ==========================================
# BACKEND INITIALIZATION (Cached for Streamlit)
# ==========================================
@st.cache_resource
def init_backend():
    """Initializes the backend only once and caches it across Streamlit reruns."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not mongo_uri or not db_name:
        logger.warning("MongoDB not configured - saving reports as CSV in cleaned/")
        report_store = CsvReportStore()
    else:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        try:
            client.admin.command("ping")
            logger.info("Connected to MongoDB database '%s'", db_name)
            report_store = MongoReportStore(client[db_name]["reports"])
        except PyMongoError as err:
            logger.warning("Cannot connect to MongoDB (%s) - saving reports as CSV in cleaned/", err)
            report_store = CsvReportStore()

    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)
    
    return data_manager, pipeline

# ==========================================
# CONSOLE RUNNER
# ==========================================
def run_console():
    """Text menu in the terminal (used by Docker)."""
    data_manager, pipeline = init_backend()
    logging.getLogger().setLevel(logging.WARNING)
    from io_manager.io_manager import IOManager
    io_manager = IOManager(data_manager)
    io_manager.main_menu(process_callback=pipeline.process)

# ==========================================
# APPLICATION ROUTING
# ==========================================
if __name__ == "__main__":
    if "--console" in sys.argv:
        run_console()
    else:
        # Check if we are running inside the Streamlit environment
        import streamlit.runtime
        if streamlit.runtime.exists():
            # We are inside Streamlit - render the GUI
            data_manager, pipeline = init_backend()
            from io_manager.gui_view_streamlit import render_streamlit_ui
            render_streamlit_ui(data_manager, pipeline)
        else:
            # We are running via standard `python main.py`. Auto-launch Streamlit.
            import subprocess
            subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])