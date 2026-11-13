import logging
import os
import subprocess
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
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not mongo_uri or not db_name:
        logger.warning("MongoDB not configured - saving reports as CSV in cleaned/")
        return CsvReportStore()

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
    except PyMongoError as err:
        logger.warning("Cannot connect to MongoDB (%s) - saving reports as CSV in cleaned/", err)
        return CsvReportStore()

    logger.info("Connected to MongoDB database '%s'", db_name)
    return MongoReportStore(client[db_name]["reports"])


def init_backend():
    """Initializes backend managers as a plain Python function (no Streamlit dependency)."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)

    report_store = build_report_store(logger)
    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    return data_manager, pipeline


def run_console():
    """Text menu in the terminal (used by Docker)."""
    data_manager, pipeline = init_backend()
    logging.getLogger().setLevel(logging.WARNING)
    from io_manager.io_manager import IOManager
    io_manager = IOManager(data_manager)
    io_manager.main_menu(process_callback=pipeline.process)


def run_streamlit():
    """Streamlit web UI (only called once inside an active ScriptRunContext)."""
    import streamlit as st
    from io_manager.gui_view_streamlit import render_streamlit_ui

    @st.cache_resource
    def get_cached_backend():
        return init_backend()

    data_manager, pipeline = get_cached_backend()
    render_streamlit_ui(data_manager, pipeline)


if __name__ == "__main__":
    if "--console" in sys.argv:
        run_console()
    elif "streamlit" in sys.modules:
        run_streamlit()
    else:
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])