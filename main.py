from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import string
import random
import uuid
from datetime import timedelta
import json
from connectors import user_collection,notes_collection,algoindex
from authutils import oauth2_scheme,create_jwt_token,get_current_user_from_header,validate_user
from utils import parse_json
from concepts import User, UserInput, NotesInput, UserName
from fetcher import validate_user_password, save_user, save_notes_user_relation
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root( current_user : User = Depends(get_current_user_from_header)):
    return {"message": "Hello World"}


@app.get("/users")
def users():
    from fetcher import all_users
    x =  all_users()
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/notes")
def getnoteslist( current_user : User = Depends(get_current_user_from_header) ):
    from fetcher import all_notes
    # take auth token and pass into all_notes()
    # current_user = get_current_user()
    print(current_user)
    x =  all_notes(current_user)
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/notes/{noteID}")
def getnotesbyid(noteID):
    from fetcher import notes_by_id
    # take auth token and the id of the notes a nd pass into all_notes()
    x = notes_by_id(str(noteID))
    if x is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/search_quick")
async def search_quick(q: str, current_user= Depends( get_current_user_from_header)):
    """
    Search for notes based on keywords for the authenticated user using Algoliasearch.

    Parameters:
    - q (str): The search query/keyword.
    - current_user (dict): The authenticated user obtained from the OAuth2 token.

    Returns:
    - List[dict]: A list of notes matching the search query.
    """
    # Algoliasearch client


    # Perform a search using Algoliasearch
    search_result = algoindex.search(q)

    # 
    from connectors import db
    all_notesID_user_can_view = [ i['notes_id'] for i in list(db.notes_users.find({ 'username' : current_user}))]
    result = []
    for i in search_result['hits']:
        if i['objectID'] in all_notesID_user_can_view:
            result.append(i) 
    print( all_notesID_user_can_view)
    # Transform Algoliasearch result to a list of dictionaries
    # filtered_notes = [
    #     {"id": note["objectID"], "title": note["title"], "content": note["content"]}
    #     for note in search_result["hits"]
    # ]

    return result



@app.get("/search_mongo")
async def search_mongo(q: str, current_user= Depends( get_current_user_from_header)):
    """
    Search for notes based on keywords for the authenticated user using Algoliasearch.

    Parameters:
    - q (str): The search query/keyword.
    - current_user (dict): The authenticated user obtained from the OAuth2 token.

    Returns:
    - List[dict]: A list of notes matching the search query.
    """
    # Algoliasearch client
    from connectors import db

    regex_pattern = f'.*{q}.*'

    # Search for documents where notes_text contains the keyword
    query = {'notes_content': {'$regex': regex_pattern, '$options': 'i'}}  # 'i' for case-insensitive search
    search_result = list(notes_collection.find(query,{'_id': 0}))

    # Perform a search using Algoliasearch

    # 
    all_notesID_user_can_view = [ i['notes_id'] for i in list(db.notes_users.find({ 'username' : current_user}))]
    result = []
    for i in search_result:
        if 'objectID' in i and i['objectID'] in all_notesID_user_can_view:
            result.append(i) 
    print( 'all_notesID_user_can_view', all_notesID_user_can_view)
    # Transform Algoliasearch result to a list of dictionaries
    # filtered_notes = [
    #     {"id": note["objectID"], "title": note["title"], "content": note["content"]}
    #     for note in search_result["hits"]
    # ]

    return result

@app.post("/signup")
def read_user(item: UserInput ):
    try:
        new_user = {
            'username' : item.username,
            'password' : item.password,
        }
        result = save_user(new_user)

        # Return a response with the inserted note's ID
        return {"message": "User saved successfully", "user": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/savenotes")
def read_notes(item: NotesInput, current_user: User = Depends( get_current_user_from_header )) :
    print('item: %s' % item)
    if True:
        notes_content = item.notes_content
        notes_id  = str(uuid.uuid4())
        new_note = {
            'objectID' : notes_id,
            'notes_content': notes_content,
            'topics' : notes_content.split(' ')
        }
        # Insert the note into the MongoDB collection
        

        result = save_notes_user_relation(current_user, notes_id, new_note)
        algoindex.save_objects([new_note] )
        # algoindex.wait_task(algoindex.save_objects([new_note])["taskID"])
        # Return a response with the inserted note's ID
        return {"message": "Note saved successfully", "note_id": str(result.inserted_id)}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@app.put("/notes/{noteID}")
async def update_note(
    noteID: str,
    item: NotesInput,
    current_user: dict = Depends(get_current_user_from_header)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"note_id": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update the note with the new data
    updated_data = {
        "$set": {
            "notes_content": item.notes_content,
        }
    }
    notes_collection.update_one({"objectID": noteID}, updated_data)
    return {"message": "Note updated successfully"}

@app.delete("/notes/{noteID}")
async def delete_note(
    noteID: str,
    current_user: dict = Depends(get_current_user_from_header)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"note_id": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Delete the note
    notes_collection.delete_one({"note_id": noteID})

    from connectors import db
    db.notes_users.delete_all({'notes_id' : noteID})

    return {"message": "Note deleted successfully"}


@app.post("/notes/{noteID}/share")
async def share_note(
    noteID: str,
    user_to_share_with: UserName,
    current_user: dict = Depends(get_current_user_from_header)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"objectID": str(noteID)})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    from connectors import db
    db.notes_users.insert_one({ 'username' : user_to_share_with.username, 'notes_id' : noteID})

    raise HTTPException(status_code=400, detail=f"{user_to_share_with.username} is already allowed to access the note")




# Endpoint to generate an access token
@app.post("/login")
def login( item: UserInput):
    # Check user credentials (replace this with your authentication logic)
    if validate_user_password(item.username, item.password):
        # Generate a JWT token with a 15-minute expiration time
        access_token_expires = timedelta(minutes=15)
        access_token = create_jwt_token(data={"sub": item.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        print('got error')
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)