import logging
import sys

from dotenv import load_dotenv

import io_manager
from ai_manager import AIManager
from moderationpipeline import ModerationPipeline
from providerfactory import ProviderFactory

if __name__ == "__main__":
    load_dotenv()  # Load API keys from .env
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        provider = ProviderFactory.from_env()
    except ValueError as err:
        logger.error("Cannot start: %s", err)
        sys.exit(1)

    pipeline = ModerationPipeline(AIManager(provider))
    io_manager.main_menu(process_callback=pipeline.process)