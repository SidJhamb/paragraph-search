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
cd paragraph-search
docker-compose run --rm app sh -c "python manage.py test"
```

## Technology Stack
* Web framework : Django, Django REST framework
* Database : PostgreSQL
* Programming Language : Python
* Containerization : Docker, docker-compose
* CI/CD platform : Github Actions

## GitHub Actions
GitHub actions are enabled for merges to the source code repository, and they automate the execution of following
tasks.
* Running Unit Tests.
* Running Linting checks by leveraging the [flake8](https://pypi.org/project/flake8/) module.

## Source Code Structure
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
docker-compose.yml         // Docker compose configuration file.
Dockerfile                 // The Dockerfile
requirements.dev.txt       // The file enlisting python module requirements for DEV environment.
requirements.txt           // The file enlisting python module requirements.

```

## Swagger Documentation
The Swagger documentation, as per the OpenAPI Specification, can be accessed at `http://127.0.0.1:8000/docs/`, after
`docker-compose up` has run successfully.

## REST API

The following REST API endpoints are exposed on the localhost after `docker-compose up` has run 
successfully and started serving the paragraph search service.

### **/paragraph/get**
This fetches 1 paragraph from [http://metaphorpsum.com/](http://metaphorpsum.com/) with 50 sentences and stores it 
as an instance of `Paragraph` model defined in [models.py](/app/core/models.py)

##### Sample Request
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

### **/paragraph/search/**
* This searches through the stored paragraphs, and allows filtering based on the query parameters.
* For query parameters, we can provide comma separated words (`?words=word1,word2..`) and one of the 
  two operators: **or** or **and** (`&operator=`). For example,
  * Words `one`, `two`, `three`, with the `or` operator should return any paragraphs that
  have at least one of the three words.
  * Words `one`, `two`, `three`, with the `and` operator should return paragraphs that have
  all the three words.
* If no query parameters are provided, then the API returns all the paragraphs stored in the database.
* If query parameters are present, then providing both in the URL, i.e `words` and `operator`, is mandatory. If only 
  either one is provided, it is considered as a Bad Request.

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
* This returns the definition of the top 10 words (frequency wise) found in all the paragraphs currently stored in 
  the database.
* Word definition is retrieved from [https://dictionaryapi.dev/](https://dictionaryapi.dev/).

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