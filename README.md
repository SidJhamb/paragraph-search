# Paragraph Search Service

This is the source code of a Paragraph Search Service serving a REST API.

## Prerequisites
Following are the **prerequisites** that need to be installed beforehand.
* Docker

## Setup
Execute the following commands from the root directory of the project to run the service.
```
cd paragraph-search
docker-compose build
docker-compose up
```

This starts a server on `localhost 127.0.0.1` listening to port `8000`.

## Unit Tests
Execute the following command from the root directory of the project to run unit tests.
```
docker-compose run --rm app sh -c "python manage.py test"
```

## Structure
```
app                       
  ├── app                  // Root Django project
  │   ├── ...
  │   ├── settings.py      // Django settings file
  │   └── urls.py          // URL mappings for the app
  ├── core                 // Django App encapsulating custom management commands and databade models.
  │   ├── management        
  │   │   ├── commands/    // Custom management commands
  │   ├── migrations/      // Django migrations
  │   ├── tests/           // Unit tests for models
  │   └── models.py        // Database models
  ├── paragraph            // Django App serving paragraph search.
  │   ├── tests/           // Unit tests for paragraph API
  │   ├── api_client.py    // Wrapper for issuing requests to external APIs.
  │   ├── serializers.py   // Django serializers.
  │   └── views.py         // View handlers to serve API requests.
  └── manage.py
  └── .flake8
.gitignore
.dockerignore
docker-compose.yml
Dockerfile
requirements.dev.txt
requirements.txt

```

## REST API

The following REST API endpoints are exposed on the localhost after `docker-compose up` has run 
successfully and started serving the paragraph search service.

### **/paragraph/get**
This fetches 1 paragraph from [http://metaphorpsum.com/](http://metaphorpsum.com/) with 50 sentences and stores it 
as an instance of `Paragraph` model defined in [models.py](/app/core/models.py)

#### Sample Request
```
curl --location --request GET 'http://127.0.0.1:8000/paragraph/get'
```

##### Sample Response
```
GET /paragraph/get HTTP/1.1" 201 3245

{
    "id": 1,
    "text": "tumbling stranger is an athlete.....
} 
```

##### **/paragraph/search/**
* Search through stored paragraphs 
* Allow providing multiple words (`?words=`) and one of the two operators: **or** or **and** (`&operator=`). For example,
  * Words `one`, `two`, `three`, with the `or` operator should return any paragraphs that
  have at least one of the three words.
  * Words `one`, `two`, `three`, with the `and` operator should return paragraphs that have
  all the three words.

##### Sample Request
```
curl --location --request GET 'http://127.0.0.1:8000/api/paragraph/search?words=assumed&operator=and'
```

##### Sample Response
```
GET /paragraph/search/?words=assumed&operator=and HTTP/1.1" 200 74999

[
    {
        "id": 1,
        "text": ....
    },
    {
        "id": 4,
        "text": ....
    },
    ...
]
```

### **/paragraph/dictionary/**
* Returns the definition of the top 10 words (frequency) found in the all the paragraphs currently store in the system.
* Word definition should retrieved from [https://dictionaryapi.dev/](https://dictionaryapi.dev/).

##### Sample Request
```
curl --location --request GET 'http://127.0.0.1:8000/paragraph/dictionary'
```

##### Sample Response
```
GET /paragraph/dictionary HTTP/1.1" 200 30751

{
    "a": [
        {
            "word": "a",
            "phonetic": "/æɪ/",
            "phonetics": [
            ....
        }
    ],
    "is": [
    ],
    ...
```