# Introduction

# High Level Architecture

# Technologies Used

API Coding Language, Python
RESTFul API Framework, Fast API
Database, MongoDB
Indexing, Algolia
Testing framework, pytest

The code language is choosed as Python for the following reasons:
- Easy onboarding of new developers
- quick prototyping

For storing the information, mongodb is used.
- It allows flexible regex and index creation for implementing basic searching functionality.

For Rate limiter, the code uses Redis cache to support rate limiting functionality.

The search feature is implemented in two apis
- /get search
The api uses mongodb to retrieve the search results. Here the content is used to create index results
Moreover to supprt word search a list of keywords in the notes expect the stop words could be used.
"This is a good note" -> topics: ["good", "note"]

- /get search_quick
The api uses algolia which is based on elasticsearch to also store the data and provide a fast search result.


# API Endpoints

Authentication Endpoints

    - [x] POST /api/auth/signup: create a new user account.
    - [x]POST /api/auth/login: log in to an existing user account and receive an access token.

Note Endpoints

    - [x] GET /api/notes: get a list of all notes for the authenticated user.
    - [x] GET /api/notes/ get a note by ID for the authenticated user.
    - [x] POST /api/notes: create a new note for the authenticated user.
    - [x] PUT /api/notes/ update an existing note by ID for the authenticated user.
    - [x] DELETE /api/notes/ delete a note by ID for the authenticated user.
    - [x] POST /api/notes/:id/share: share a note with another user for the authenticated user.
    - [x] GET /api/search?q=:query: search for notes based on keywords for the authenticated user.
    - [x]   GET /api/search_quick?q=:query: search for notes for user using elasticsearch.

# POC API Testing UI
    - Link to UI used for demo: 
    - Video URL: 
# Deploy FastAPI on Render

Use this repo as a template to deploy a Python [FastAPI](https://fastapi.tiangolo.com) service on Render.

See https://render.com/docs/deploy-fastapi or follow the steps below:

## Manual Steps

1. You may use this repository directly or [create your own repository from this template](https://github.com/render-examples/fastapi/generate) if you'd like to customize the code.
2. Create a new Web Service on Render.
3. Specify the URL to your new repository or this repository.
4. Render will automatically detect that you are deploying a Python service and use `pip` to download the dependencies.
5. Specify the following as the Start Command.

    ```shell
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```