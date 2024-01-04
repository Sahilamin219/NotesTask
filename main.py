from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import timedelta
import json
from connectors import user_collection,notes_collection,algoindex
from authutils import oauth2_scheme,create_jwt_token,get_current_user_from_header,validate_user
from utils import parse_json
from concepts import User, UserInput, NotesInput, UserName
from fetcher import validate_user_password, save_user, save_notes_user_relation, all_search_results_mongo, all_search_results_quick, delete_notes_fromDB, share_notes_with_user
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
app = FastAPI()

redis_uri = "rediss://red-cmb6u9da73kc73bq53c0:Bu7HKtv6fBLU2UaO5Rofv8THAKYHdCuT@oregon-redis.render.com:6379"
limiter = FastAPILimiter()

@app.on_event("startup")
async def on_startup():
    redis_ = redis.from_url(redis_uri, encoding="utf-8", decode_responses=True)
    await limiter.init(redis_)

@app.on_event("shutdown")
async def on_shutdown():
    await limiter.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def root( current_user : User = Depends(get_current_user_from_header)):
    return {"message": "Hello World"}


@app.post("/api/auth/signup", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def read_user(item: UserInput ):
    """
    Create a new user.

    Parameters:
    - `item`: UserInput model containing 'username' and 'password' fields.

    Returns:
    - A JSON response indicating the success or failure of the user creation.
      - If successful, returns {"message": "User saved successfully", "user": "inserted_id"}.
      - If an error occurs, raises an HTTPException with a 500 status code and the error message.
    """
    try:
        new_user = {
            'username' : item.username,
            'password' : item.password,
        }
        result = save_user(new_user)

        return {"message": "User saved successfully", "user": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/login", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def login( item: UserInput):
    """
    Authenticate and generate access token for a user.

    Parameters:
    - `item`: UserInput model containing 'username' and 'password' fields.

    Returns:
    - A JSON response containing an access token if authentication is successful.
      - If successful, returns {"access_token": "token_value", "token_type": "bearer"}.
      - If authentication fails, raises an HTTPException with a 401 status code and "Invalid credentials" detail.
    """
    if validate_user_password(item.username, item.password):
        access_token_expires = timedelta(minutes=15)
        access_token = create_jwt_token(data={"sub": item.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        print('got error')
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})


@app.get("/api/notes", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def getnoteslist( current_user : User = Depends(get_current_user_from_header) ):
    """
    Get a list of notes for the authenticated user.

    Parameters:
    - `current_user`: User model obtained from the authentication header.

    Returns:
    - A JSON response containing the list of notes for the authenticated user.
    - Raises an HTTPException with a 404 status code if no notes are found.
    """
    from fetcher import all_notes
    print(current_user)
    x =  all_notes(current_user)
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/api/notes/{noteID}", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def getnotesbyid(noteID):
    """
    Get a specific note by its ID.

    Parameters:
    - `noteID`: The ID of the note to retrieve.

    Returns:
    - A JSON response containing the content of the specified note.
    - Raises an HTTPException with a 404 status code if the note is not found.
    """
    from fetcher import notes_by_id
    x = notes_by_id(str(noteID))
    if x is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.post("/api/notes", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def read_notes(item: NotesInput, current_user: User = Depends( get_current_user_from_header )) :
    """
    Create a new note for the authenticated user.

    Parameters:
    - `item`: NotesInput model containing the 'notes_content'.
    - `current_user`: User model obtained from the authentication header.

    Returns:
    - A JSON response indicating the success or failure of the note creation.
      - If successful, returns {"message": "Note saved successfully", "note_id": "inserted_id"}.
      - If an error occurs, raises an HTTPException with a 500 status code and the error message.
    """
    try:
        notes_content = item.notes_content
        notes_id  = str(uuid.uuid4())
        new_note = {
            'objectID' : notes_id,
            'notes_content': notes_content,
            'topics' : notes_content.split(' ')
        }
        print('current_user: ',current_user)

        result = save_notes_user_relation(current_user, notes_id, new_note)
        algoindex.save_objects([new_note] )
        return {"message": "Note saved successfully", "note_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notes/{noteID}", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def update_note(
    noteID: str,
    item: NotesInput,
    current_user: dict = Depends(get_current_user_from_header)
):
    """
    Update an existing note by its ID.

    Parameters:
    - `noteID`: The ID of the note to update.
    - `item`: NotesInput model containing the updated 'notes_content'.
    - `current_user`: User model obtained from the authentication header.

    Returns:
    - A JSON response indicating the success of the note update.
      - If successful, returns {"message": "Note updated successfully"}.
      - Raises an HTTPException with a 404 status code if the note is not found.
    """
    existing_note = notes_collection.find_one({"objectID": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    updated_data = {
        "$set": {
            "notes_content": item.notes_content,
        }
    }
    notes_collection.update_one({"objectID": noteID}, updated_data)
    return {"message": "Note updated successfully"}


@app.delete("/notes/{noteID}", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def delete_note(
    noteID: str,
    current_user: dict = Depends(get_current_user_from_header)
):
    """
    Delete a note by its ID.

    Parameters:
    - `noteID`: The ID of the note to delete.
    - `current_user`: User model obtained from the authentication header.

    Returns:
    - A JSON response indicating the success of the note deletion.
      - If successful, returns the result of the delete_notes_fromDB function.
      - Raises an HTTPException with a 404 status code if the note is not found.
    """
    existing_note = notes_collection.find_one({"objectID": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    return delete_notes_fromDB(noteID)


@app.post("/api/notes/{noteID}/share", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def share_note(
    noteID: str,
    user_to_share_with: UserName,
    current_user: dict = Depends(get_current_user_from_header)
):
    """
    Share a note with another user.

    Parameters:
    - `noteID`: The ID of the note to share.
    - `user_to_share_with`: UserName model containing the username of the user to share the note with.
    - `current_user`: User model obtained from the authentication header.

    Raises:
    - HTTPException with a 404 status code if the note is not found.
    """
    existing_note = notes_collection.find_one({"objectID": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    share_notes_with_user(noteID, user_to_share_with)

@app.get("api/search_quick", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def search_quick(q: str, current_user= Depends( get_current_user_from_header)):
    """
    Search for notes based on keywords for the authenticated user using Algoliasearch.

    Parameters:
    - q (str): The search query/keyword.
    - current_user (dict): The authenticated user obtained from the OAuth2 token.

    Returns:
    - List[dict]: A list of notes matching the search query.
    """
    return all_search_results_quick(q, current_user)



@app.get("api/search", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
async def search_mongo(q: str, current_user= Depends( get_current_user_from_header)):
    """
    Search for notes based on keywords for the authenticated user using Algoliasearch.

    Parameters:
    - q (str): The search query/keyword.
    - current_user (dict): The authenticated user obtained from the OAuth2 token.

    Returns:
    - List[dict]: A list of notes matching the search query.
    """
    return all_search_results_mongo(q, current_user)


@app.get("/users", dependencies=[Depends(RateLimiter(times=10, seconds=30))])
def users():
    from fetcher import all_users
    x =  all_users()
    return json.loads(json.dumps({"content": list(x)}, default=str))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)