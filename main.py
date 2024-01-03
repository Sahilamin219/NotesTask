from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import requests
import jwt
import string
import random

origins = [
    "*"
]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pymongo import MongoClient

uri = "mongodb+srv://dev:pass@cluster0.qndd2.mongodb.net/?retryWrites=true&w=majority"
# uri = "mongodb+srv://dev:664710@cluster0.qndd2.mongodb.net/timizli?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["timizli"]
notes_collection = db["notes"]
note_id = 0

GOOGLE_CLIENT_ID="317891675877-rkevale6gfphf9jj9tdcnoeoem4ar0jg.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from bson import json_util
import json
def parse_json(data):
    return json.loads(json_util.dumps(data))

import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# acess token will be passed
def get_current_user():    
    return "sahil"

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users")
def users():
    from fetcher import all_users
    x =  all_users()
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/notes")
def getnoteslist():
    from fetcher import all_notes
    # take auth token and pass into all_notes()
    current_user = get_current_user()
    x =  all_notes(current_user)
    return json.loads(json.dumps({"content": list(x)}, default=str))

@app.get("/notes/{noteID}")
def getnotesbyid(noteID: int):
    from fetcher import notes_by_id
    # take auth token and the id of the notes a nd pass into all_notes()
    x =  notes_by_id(noteID)
    return json.loads(json.dumps({"content": list(x)}, default=str))

# keywords will be passed to search notes
@app.get("search?q=:query:")
def getnotesby():
    from fetcher import notes_by_search_query
    # take auth token and the id of the notes and pass into all_notes()
    x =  notes_by_search_query()
    return json.loads(json.dumps({"content": list(x)}, default=str))



from pydantic import BaseModel

class UserInputStructure(BaseModel):
    username: str
    user_email: str
    password: str
    token: str

class NotesInputStructure(BaseModel):
    notes_title: str
    notes_content: str
    user_owner: str
    users_allowed: list
    note_id: int

@app.post("/registeruser")
def read_item(item: UserInputStructure ):
    user_name = item.user_name
    user_email = item.user_email
    password = item.password
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


@app.post("/savenotes")
def read_item(item: NotesInputStructure ):
    notes_title = item.notes_title
    notes_content = item.notes_content
    users_allowed = item.users_allowed
    user_owner_name = get_current_user()
    new_note = {
        'notes_title': notes_title,
        'notes_content': notes_content,
        'users_allowed': users_allowed,
        'user_owner': user_owner_name,
        'note_id': note_id
    }
    note_id += 1
    # Insert the note into the MongoDB collection
    result = notes_collection.insert_one(new_note)

    # Return a response with the inserted note's ID
    return {"message": "Note saved successfully", "note_id": str(result.inserted_id)}


@app.put("/api/notes/{note_id}")
async def update_note(
    note_id: str,
    item: NotesInputStructure,
    current_user: dict = Depends(get_current_user)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"note_id": note_id})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Check if the authenticated user has permission to update the note
    if current_user["username"] not in existing_note["users_allowed"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Update the note with the new data
    updated_data = {
        "$set": {
            "notes_title": item.notes_title,
            "notes_content": item.notes_content,
            "users_allowed": item.users_allowed,
            "user_owner": item.user_owner
        }
    }
    notes_collection.update_one({"_id": note_id}, updated_data)

    return {"message": "Note updated successfully"}

@app.delete("/api/notes/{note_id}")
async def delete_note(
    note_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"_id": note_id})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Check if the authenticated user has permission to delete the note
    if current_user["username"] not in existing_note["users_allowed"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Delete the note
    notes_collection.delete_one({"_id": note_id})

    return {"message": "Note deleted successfully"}


@app.post("/api/notes/{note_id}/share")
async def share_note(
    note_id: str,
    user_to_share_with: str,
    current_user: dict = Depends(get_current_user)
):
    # Check if the note exists
    existing_note = notes_collection.find_one({"_id": note_id})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Check if the authenticated user has permission to share the note
    if current_user["username"] not in existing_note["users_allowed"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Check if the user to share with exists
    if user_to_share_with not in existing_note["users_allowed"]:
        existing_note["users_allowed"].append(user_to_share_with)

        # Update the note with the new list of allowed users
        updated_data = {
            "$set": {
                "users_allowed": existing_note["users_allowed"]
            }
        }
        notes_collection.update_one({"_id": note_id}, updated_data)

        return {"message": f"Note shared with {user_to_share_with} successfully"}

    raise HTTPException(status_code=400, detail=f"{user_to_share_with} is already allowed to access the note")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)