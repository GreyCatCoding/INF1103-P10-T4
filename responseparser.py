"""Turns the model's reply text into a dict, removing a markdown code fence if present. Returns None if the text is not valid JSON."""
import json


class ResponseParser:
    """Converts the provider model's JSON string into a dict."""

    def parse(self, raw_response: str) -> dict | None:
        """Returns the parsed dict, or None if the reply isn't valid JSON."""
        raw_response = raw_response.strip()

   
        if raw_response.startswith("```"): # remove a markdown fence if the model added one
            raw_response = raw_response.strip("`") # removes the surrounding backticks
            if raw_response.startswith("json"):
                raw_response = raw_response[len("json"):] # remove the language label

        try:
            return json.loads(raw_response) # json.loads ignores leftover whitespace
        except (json.JSONDecodeError, TypeError):
            return None