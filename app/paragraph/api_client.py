import requests

PARAGRAPH_URL = "http://metaphorpsum.com/paragraphs/1/50"
DEFINITION_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


def get_paragraph():
    try:
        response = requests.get(PARAGRAPH_URL)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        return response.text
    except Exception:
        raise


def get_word_definition(word):
    try:
        response = requests.get(DEFINITION_URL + word)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        return response.json()
    except Exception:
        raise
