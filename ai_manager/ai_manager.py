"""Sends one comment record through prompt, AI call, parse and validate, retrying once on failure. 
Returns the record with the AI verdict added, or None if every attempt fails."""
import logging

from aiprovider import AIProvider
from promptbuilder import PromptBuilder
from responseparser import ResponseParser
from responsevalidator import ResponseValidator

logger = logging.getLogger(__name__)


class AIManager:
    """build -> generate -> parse -> validate, with retries."""

    __COMMENTS_FIELD = "processed_comments"
    __ID_FIELD = "User ID"

    def __init__(self, provider: AIProvider, max_retries: int = 1):
        self.__provider = provider
        self.__max_retries = max_retries
        self.__builder = PromptBuilder()
        self.__parser = ResponseParser()
        self.__validator = ResponseValidator()

    def analyse_record(self, record: dict) -> dict | None:
        """Returns the record merged with the AI verdict, or None if every attempt failed."""
        comment = record.get(self.__COMMENTS_FIELD)
        if not isinstance(comment, str) or not comment.strip():
            logger.error("Record %s has no usable '%s'", record.get(self.__ID_FIELD), self.__COMMENTS_FIELD)
            return None

        # Build prompt
        prompt = self.__builder.build(record)
        # First try plus MAX_RETRIES retries
        for attempt in range(self.__max_retries + 1):
            # Get raw response from the main provider or OpenRouter if the main provider fails
            raw_response = self.__provider.generate(self.__builder.system_prompt, prompt)
            if not raw_response:
                logger.info("Attempt %s: Call API failed", attempt + 1)
                # Try calling API again on the next attempt
                continue

            # Parse raw response
            data = self.__parser.parse(raw_response)
            if not data:
                logger.info("Attempt %s: Parse response failed", attempt + 1)
                # Get new reply from the API on the next attempt
                continue

            if self.__validator.validate(data):
                # Merge record dictionary and data dictionary; return original record with AI verdict
                return {**record, **data}
            logger.info("Attempt %s: Reply failed validation", attempt + 1)

        # If all attempts failed, log which record and give up
        logger.warning("Failed to analyse record %s after %s attempts", record.get(self.__ID_FIELD), self.__max_retries + 1)
        return None
