"""Cleans a single comment: lowercase, expand slang, strip URLs/emails/symbols, tidy spaces."""
import re


class TextCleaner:
    """Standardises comment text so the AI receives consistent and readable input."""

    # Shared by every TextCleaner unless a custom dictionary is passed in (static, private)
    __DEFAULT_SLANG = {
        "lol": "laugh out loud", "sybau": "shut your bitch ass up", "imo": "in my opinion",
        "imho": "in my humble opinion", "tbh": "to be honest", "smh": "shaking my head",
        "fk": "fuck", "btw": "by the way", "idk": "i do not know", "omg": "oh my god",
        "ur": "your", "r": "are", "u": "you", "rfc": "request for comments",
    }

    def __init__(self, slang_dict: dict[str, str] | None = None):
        """Initializes the TextCleaner with a custom slang dictionary or the default one."""

        # check if a custom slang dictionary was provided
        if slang_dict is None:
            slang_dict = TextCleaner.__DEFAULT_SLANG

        # Referencing the dictionary above
        self.__slang_dict = dict(slang_dict)

        # Longest slang first so longer words are tried before shorter ones (e.g. "imho" before "imo")
        sorted_slang = sorted(self.__slang_dict.keys(), key=len, reverse=True)
        escaped_slang = []
        for word in sorted_slang:
            escaped_slang.append(re.escape(word))

        # cleaning of slang words and unwanted noise in the text
        # regex to match any slang word in the dictionary and replace with corresponding values in dictionary
        self.__slang_pattern = re.compile(r"\b(" + "|".join(escaped_slang) + r")\b", flags=re.IGNORECASE)
        # regex to match URLs , emails and unwanted symbols
        self.__noise_pattern = re.compile(r"https?://\S+|www\.\S+|\S+@\S+|[^a-zA-Z0-9$*@!\s]")

    def clean(self, text: str) -> str:
        """Returns the cleaned comment, or "" if text is not a string or is blank."""
        if not isinstance(text, str) or not text.strip():
            return ""

        text = text.lower()
        text = self.__slang_pattern.sub(self.__expand_slang, text)
        text = self.__noise_pattern.sub("", text)
        return " ".join(text.split())  # Collapse repeated spaces and newlines into single spaces

    def __expand_slang(self, match: re.Match) -> str:
            """Returns the full phrase for one matched slang word."""
            slang_word = match.group(0).lower()
            return self.__slang_dict[slang_word]
    