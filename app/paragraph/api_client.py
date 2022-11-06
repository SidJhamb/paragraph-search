import requests

PARAGRAPH_URL = "http://metaphorpsum.com/paragraphs/1/50"
DEFINITION_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


def get_paragraph():
    try:
        response = requests.get(PARAGRAPH_URL)
        response.raise_for_status()
        return response.text
    except Exception:
        raise


def get_word_definition(word):
    response = requests.get(DEFINITION_URL + word)

    if response.status_code != 200 and response.status_code != 404:
        raise Exception("Error while processing the API request to https://dictionaryapi.dev/.")

    return response.json()
