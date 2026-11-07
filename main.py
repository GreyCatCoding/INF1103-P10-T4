import logging
import sys
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication

from data_manager import DataManager
from moderationpipeline import ModerationPipeline
from providerfactory import ProviderFactory
from csvreportstore import CsvReportStore
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

    # 1. Initialize your existing OOP backend systems
    report_store = CsvReportStore()
    data_manager = DataManager(report_store)
    pipeline = ModerationPipeline(AIManager(provider), data_manager)

    # 2. Start the PySide6 Application Loop
    app = QApplication(sys.argv)
    
    # 3. Create the GUI Window, passing the backend dependencies
    #    (pipeline.process gets passed as the callback just like before)
    window = GUIView(data_manager=data_manager, process_callback=pipeline.process)
    window.show()
    
    # 4. Safely execute the application and exit when closed
    sys.exit(app.exec())