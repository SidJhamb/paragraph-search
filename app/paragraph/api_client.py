import requests

PARAGRAPH_URL = "http://metaphorpsum.com/paragraphs/1/50"
DEFINITION_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


def get_paragraph():
    response = requests.get(PARAGRAPH_URL)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_word_definition(word):
    response = requests.get(DEFINITION_URL + word)
    return response.json()
