"""Tests for TextCleaner: each test checks one cleaning rule."""
from io_manager.textcleaner import TextCleaner

def test_changes_text_to_lowercase():
    # Prepare: create the object we want to test
    cleaner = TextCleaner()

    # Run: call the method we want to test
    result = cleaner.clean("HELLO World")

    # Check: compare the actual result with the result we expect
    assert result == "hello world"


# ---------- Slang ----------

def test_expands_slang_words():
    cleaner = TextCleaner()

    result = cleaner.clean("u r late")

    # "u" becomes "you" and "r" becomes "are"
    assert result == "you are late"


def test_expands_slang_in_capital_letters():
    cleaner = TextCleaner()

    result = cleaner.clean("IMHO this is fine")

    # Capital letters should not stop the slang from being found
    assert result == "in my humble opinion this is fine"


def test_only_replaces_whole_slang_words():
    cleaner = TextCleaner()

    result = cleaner.clean("rain")

    # "r" is slang, but the "r" inside "rain" must not become "are"
    # Otherwise the result would be "areain"
    assert result == "rain"


def test_can_use_a_custom_slang_dictionary():
    # Pass in our own dictionary instead of using the default one
    cleaner = TextCleaner({"gg": "good game"})

    result = cleaner.clean("gg lol")

    # "gg" is in our dictionary, so it is expanded
    # "lol" is only in the default dictionary, so it stays the same
    assert result == "good game lol"


# ---------- Noise (links, emails and symbols) ----------

def test_removes_website_links():
    cleaner = TextCleaner()

    result = cleaner.clean("visit https://spam.com or www.spam.com now")

    assert result == "visit or now"


def test_removes_email_addresses():
    cleaner = TextCleaner()

    result = cleaner.clean("email amy@test.com today")

    assert result == "email today"


def test_removes_unwanted_symbols_but_keeps_allowed_ones():
    cleaner = TextCleaner()

    result = cleaner.clean("wow!! $100 #deal :)")

    # Removed: # : )
    # Kept: ! and $ (the cleaner also keeps * and @)
    assert result == "wow!! $100 deal"


# ---------- Spaces ----------

def test_tidies_extra_spaces_and_new_lines():
    cleaner = TextCleaner()

    result = cleaner.clean("  too    many\n  spaces  ")

    assert result == "too many spaces"


# ---------- Invalid input ----------

def test_blank_text_returns_empty_string():
    cleaner = TextCleaner()

    result = cleaner.clean("     ")

    assert result == ""


def test_non_text_input_returns_empty_string():
    cleaner = TextCleaner()

    # clean() should return "" instead of crashing when it does not receive text
    assert cleaner.clean(None) == ""
    assert cleaner.clean(123) == ""


# ---------- All the rules together ----------

def test_applies_all_rules_together():
    cleaner = TextCleaner()

    result = cleaner.clean("U   r SO funny lol!! www.spam.com")

    # Lowercase + slang expanded + link removed + extra spaces tidied
    assert result == "you are so funny laugh out loud!!"
