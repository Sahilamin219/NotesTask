# Introduction
    - Video URL: 

https://github.com/Sahilamin219/NotesTask/assets/48405411/192ecfb3-9a51-43c6-88a0-ff18126581d7
# High Level Architecture
![notes-high-level drawio](https://github.com/Sahilamin219/NotesTask/assets/48405411/21fe3d7d-1d40-4d1d-8d15-e74bdddec50c)


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
![signup](https://github.com/Sahilamin219/NotesTask/assets/48405411/5a197a54-3c0e-470b-b5c8-c505abb431dd)

    - [x] POST /api/auth/login: log in to an existing user account and receive an access token.
![login](https://github.com/Sahilamin219/NotesTask/assets/48405411/5faf32cd-e34d-4f7f-b79c-cd066e46ec13)


Note Endpoints

    - [x] GET /api/notes: get a list of all notes for the authenticated user.
![allnotesapi](https://github.com/Sahilamin219/NotesTask/assets/48405411/50db3a5b-f499-41e1-b2a2-1bb2e9164d28)

    - [x] GET /api/notes/ get a note by ID for the authenticated user.
![byid](https://github.com/Sahilamin219/NotesTask/assets/48405411/187d920a-201a-4c9e-bbe4-dac7d79a3419)

    - [x] POST /api/notes: create a new note for the authenticated user.
![savenotesapi](https://github.com/Sahilamin219/NotesTask/assets/48405411/ae9f668c-7ff7-42e8-b6b0-8a514c2ec35e)

    - [x] PUT /api/notes/ update an existing note by ID for the authenticated user.
![put](https://github.com/Sahilamin219/NotesTask/assets/48405411/ea128be1-4e4c-43d7-a248-d21e7d4ff55a)

    - [x] DELETE /api/notes/ delete a note by ID for the authenticated user.
![delete](https://github.com/Sahilamin219/NotesTask/assets/48405411/d1152553-00f0-425f-9115-955bee5006c1)

    - [x] POST /api/notes/:id/share: share a note with another user for the authenticated user.
![shareapi](https://github.com/Sahilamin219/NotesTask/assets/48405411/c86d82ef-d1ac-4f90-876c-201eb634698b)

    - [x] GET /api/search?q=:query: search for notes based on keywords for the authenticated user.
![searchapi](https://github.com/Sahilamin219/NotesTask/assets/48405411/78cfa0e5-5181-481d-bc50-a1d735df68f0)

    - [x] GET /api/search_quick?q=:query: search for notes for user using elasticsearch.
    











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
