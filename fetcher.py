from pymongo import MongoClient
import bcrypt
from connectors import user_collection, notes_collection, db, algoindex
from fastapi import HTTPException



def user_via_id(user_id):
    """
    Retrieve a user document from MongoDB based on user_id.

    Parameters:
    - `user_id`: Identifier for the user.

    Returns:
    - User document matching the provided user_id.
    """
    return db.users.find_one({"user_id": user_id})
    

def all_users():
    """
    Retrieve all user documents from MongoDB.

    Returns:
    - List of all user documents.
    """
    document = db.users.find()
    users_list = list(document)
    return users_list


def all_notes(current_user):
    """
    Retrieve all notes for a specific user from MongoDB.

    Parameters:
    - `current_user`: Username of the user.

    Returns:
    - List of notes for the specified user.
    """
    doc = list(db.notes_users.find({"username": current_user}))
    notes_list = list()
    for i in doc:
        notes_list.extend(list(db.notes.find({ 'objectID' : i['notes_id']})))
    print("All Users:", notes_list)
    return notes_list


def notes_by_id(note_id):
    """
    Retrieve a note from MongoDB based on its note_id.

    Parameters:
    - `note_id`: Identifier for the note.

    Returns:
    - List containing the note document with the specified note_id.
    """
    note = list(db.notes.find({"objectID" : note_id }))# find notes_by_id()
    # print("your note" , list(note), type(note_id), note_id)
    return note


def notes_by_search_query():
    """
    Retrieve all notes from MongoDB.

    Returns:
    - List of all notes.
    """
    notes_list = db.notes.find()# search by keywords
    return notes_list


def save_user_to_mongodb(username, password):
    """
    Save a new user to MongoDB.

    Parameters:
    - `username` (str): The username of the user.
    - `password` (str): The password of the user.

    Returns:
    - MongoDB insert result.
    """

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create a document to insert into the collection
    user_document = {
        'username': username,
        'hashed_password': hashed_password
    }

    # Insert the document into the collection
    result = user_collection.insert_one(user_document)

    # Print the result (optional)
    print(f"User inserted with ID: {result.inserted_id}")
    return result


def validate_user_password(username, password):
    """
    Validate user credentials.

    Parameters:
    - `username` (str): The username of the user.
    - `password` (str): The password of the user.

    Returns:
    - True if the password is correct, False otherwise.
    """
    user_document = user_collection.find_one({'username': username})

    if user_document:
        # Extract the stored hashed password from the document
        stored_hashed_password = user_document['hashed_password']

        # Check if the entered password matches the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            print("Password is correct!")
            return True
        else:
            print("Password is incorrect.")
            return False
    else:
        print("User not found.")
        return False
    

def save_user(new_user):
    """
    Save a new user to MongoDB, checking for existing username.

    Parameters:
    - `new_user` (dict): Dictionary containing 'username' and 'password'.

    Returns:
    - MongoDB insert result.
    """
    user_check = list(user_collection.find({'username' : new_user['username']}))
    if( user_check ):
        raise HTTPException(status_code=401, detail="User already exits")
    # result = user_collection.insert_one(new_user)
    result = save_user_to_mongodb(new_user['username'], new_user['password'])
    return result


def save_notes_user_relation(username, notes_id, new_note):
    """
    Save a new note and its relation to a user in MongoDB.

    Parameters:
    - `username` (str): The username of the user.
    - `notes_id` (str): The ID of the note.
    - `new_note` (dict): Dictionary containing note information.

    Returns:
    - MongoDB insert result.
    """
    result = notes_collection.insert_one(new_note)
    db.notes_users.insert_one({"username":username, "notes_id":notes_id})
    return result


def all_search_results_quick(q, current_user):
    """
    Retrieve search results from Algolia and filter notes based on user access.

    Parameters:
    - `q` (str): The search query.
    - `current_user` (str): The username of the current user.

    Returns:
    - List of search results filtered based on user access.
    """
    search_result = algoindex.search(q)

    all_notesID_user_can_view = [ i['notes_id'] for i in list(db.notes_users.find({ 'username' : current_user}))]
    result = []
    for i in search_result['hits']:
        if i['objectID'] in all_notesID_user_can_view:
            result.append(i) 

    return result


def all_search_results_mongo(q, current_user):
    """
    Retrieve search results from MongoDB based on a search query and user access.

    Parameters:
    - `q` (str): The search query.
    - `current_user` (str): The username of the current user.

    Returns:
    - List of search results filtered based on user access.
    """
    regex_pattern = f'.*{q}.*'

    query = {'notes_content': {'$regex': regex_pattern, '$options': 'i'}}  # 'i' for case-insensitive search
    search_result = list(notes_collection.find(query,{'_id': 0}))


    all_notesID_user_can_view = [ i['notes_id'] for i in list(db.notes_users.find({ 'username' : current_user}))]
    result = []
    for i in search_result:
        if 'objectID' in i and i['objectID'] in all_notesID_user_can_view:
            result.append(i) 

    return result


def delete_notes_fromDB(noteID):
    """
    Delete a note from MongoDB.

    Parameters:
    - `noteID` (str): The ID of the note to be deleted.

    Returns:
    - Dictionary indicating the success of the note deletion.
    """
    notes_collection.delete_one({"objectID": noteID})
    print('error coming')
    already_not_deleted = list(db.notes_users.find({'notes_id' : noteID}))
    print('error came', already_not_deleted)
    if already_not_deleted is not None:
        print('error actually coming')
        db.notes_users.delete_many({'notes_id' : noteID})
    return {"message": "Note deleted successfully"}


def share_notes_with_user(noteID, user_to_share_with):
    """
    Share a note with another user in MongoDB.

    Parameters:
    - `noteID` (str): The ID of the note to be shared.
    - `user_to_share_with` (UserName): UserName model containing the username of the user to share the note with.

    Returns:
    - Dictionary indicating the success of sharing the note.
    """
    existing_user = db.notes_users.find_one({ 'username' : user_to_share_with.username, 'notes_id' : noteID})
    if existing_user is not None:
        raise HTTPException(status_code=400, detail=f"{user_to_share_with.username} is already allowed to access the note")
    
    db.notes_users.insert_one({ 'username' : user_to_share_with.username, 'notes_id' : noteID})
    return {"message": "Note Shared successfully"}


