import logging

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Rejects AI API responses with missing keys, wrong types, bad values or contradictions."""
    __REQUIRED_FIELDS = {"harmful", "category", "severity", "target", "confidence", "reason"}
    __ALLOWED_CATEGORIES = {"harassment", "hate", "violence", "sexual", "self_harm", "spam", "none"}
    __ALLOWED_TARGETS = {"individual", "group", "none"}

    def validate(self, data: dict) -> bool:
        """Returns True if data is safe to pass to logic_manager."""
        # Valid JSON can still be a number, list or string; only a dict can hold the six keys
        if not isinstance(data, dict):
            logger.error("Reply is not a JSON object: %s", data)
            return False

        # If any required field is missing, log which ones and return False
        missing_fields = self.__REQUIRED_FIELDS - data.keys()
        if missing_fields:
            logger.error("Missing fields %s: %s", missing_fields, data)
            return False

        # if not means the field is either missing or of the wrong type
        if not isinstance(data.get("harmful"), bool): 
            logger.error("Harmful data is not boolean: %s",data)
            return False
        if not isinstance(data.get("category"), str) or data.get("category") not in self.__ALLOWED_CATEGORIES:
            logger.error("Category data is not valid: %s",data)
            return False

        # bools are ruled out completely
        severity = data.get("severity")
        if isinstance(severity, bool) or not isinstance(severity, int) or not (0 <= severity <= 4):
            logger.error("Severity data is not valid: %s", data)
            return False

        if not isinstance(data.get("target"), str) or data.get("target") not in self.__ALLOWED_TARGETS:
            logger.error("Target data is not valid: %s",data)
            return False

        confidence = data.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            logger.error("Confidence data is not valid: %s", data)
            return False

        if not isinstance(data.get("reason"), str) or not data.get("reason").strip():
            logger.error("Reason data is not valid: %s",data)
            return False

        # If data indicates not harmful, check for any contradictions
        if data.get("harmful") is False:
            if data.get("category") != "none" or data.get("severity") != 0 or data.get("target") != "none":
                logger.error("Not harmful but category/severity/target say otherwise: %s", data)
                return False
        # If data indicates harmful, check for any contradictions
        if data.get("harmful") is True:
            if data.get("category") == "none" or not (1 <= data.get("severity") <= 4):
                logger.error("Harmful but category is none or severity is 0: %s", data)
                return False

        return True