from aiprovider import AIProvider


class FakeProvider(AIProvider):
    """Returns the given replies in order, None on failed call."""

    def __init__(self, replies: list[str | None]):
        self.__replies = list(replies)
        self.__calls = 0

    @property
    def calls(self) -> int:
        """Number of times generate() was called."""
        return self.__calls

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        self.__calls += 1

        # if there are replies left, remove and return the first one, else return None
        if self.__replies:
            return self.__replies.pop(0)
        else:
            return None