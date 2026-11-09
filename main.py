import logging
import os
import sys
from dotenv import load_dotenv

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

    # Build the backend once
    report_store = CsvReportStore()
    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    if "--console" in sys.argv:
        run_console(data_manager, pipeline)
    else:
        run_gui(data_manager, pipeline)