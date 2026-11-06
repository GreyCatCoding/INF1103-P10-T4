class ModerationRecord:
    """One AI-analysed comment. Raises ValueError on creation if the data is invalid."""

    __REQUIRED_FIELDS = {"User ID", "username", "processed_comments", "harmful",
                         "category", "severity", "target", "confidence", "reason"}
    __TEXT_FIELDS = ["username", "processed_comments", "category", "target", "reason"]
    __ALLOWED_CATEGORIES = {"harassment", "hate", "violence", "sexual", "self_harm", "spam", "none"}
    __ALLOWED_TARGETS = {"individual", "group", "none"}

    def __init__(self, data: dict):
        self.__validate(data)  # Stops here with ValueError if data is bad
        self.__user_id = data["User ID"]
        self.__username = data["username"]
        self.__comment = data["processed_comments"]
        self.__harmful = data["harmful"]
        self.__category = data["category"].lower()
        self.__severity = data["severity"]
        self.__target = data["target"].lower()
        self.__confidence = data["confidence"]
        self.__reason = data["reason"]

    @property
    def user_id(self) -> int: return self.__user_id
    @property
    def username(self) -> str: return self.__username
    @property
    def comment(self) -> str: return self.__comment
    @property
    def harmful(self) -> bool: return self.__harmful
    @property
    def category(self) -> str: return self.__category
    @property
    def severity(self) -> int: return self.__severity
    @property
    def target(self) -> str: return self.__target
    @property
    def confidence(self) -> float: return self.__confidence
    @property
    def reason(self) -> str: return self.__reason

    def __validate(self, data: dict) -> None:
        # Ensure AI output is a dictionary
        if not isinstance(data, dict):
            raise ValueError("AI output must be a dictionary")

        # Ensure every required field is present
        for field in sorted(self.__REQUIRED_FIELDS):
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        # Ensure text fields are strings
        for field in self.__TEXT_FIELDS:
            if not isinstance(data[field], str):
                raise ValueError(f"{field} must be a string")

        # Ensure user ID is a whole number, 0 or more
        if type(data["User ID"]) is not int or data["User ID"] < 0:
            raise ValueError("User ID must be a non-negative integer")

        # Ensure username and comment are not blank
        if not data["username"].strip():
            raise ValueError("username cannot be empty")
        if not data["processed_comments"].strip():
            raise ValueError("comment cannot be empty")

        # Ensure harmful is True/False
        if type(data["harmful"]) is not bool:
            raise ValueError("harmful must be boolean")

        # Ensure severity is an int from 0 to 4
        if type(data["severity"]) is not int:
            raise ValueError("severity must be an integer")
        if not 0 <= data["severity"] <= 4:
            raise ValueError("severity must be between 0 and 4")

        # Ensure confidence is a number from 0 to 1
        if type(data["confidence"]) not in (int, float):
            raise ValueError("confidence must be numeric")
        if not 0 <= data["confidence"] <= 1:
            raise ValueError("confidence must be between 0 and 1")

        # Ensure category and target are allowed values
        if data["category"].lower() not in self.__ALLOWED_CATEGORIES:
            raise ValueError("Unknown category")
        if data["target"].lower() not in self.__ALLOWED_TARGETS:
            raise ValueError("Unknown target")