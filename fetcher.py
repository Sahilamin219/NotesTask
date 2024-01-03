from pymongo import MongoClient

uri = "mongodb+srv://dev:pass@cluster0.qndd2.mongodb.net/timizli?retryWrites=true&w=majority"
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



def user_via_id(user_id):
    return db.users.find_one({"user_id": user_id})
    

def all_users():
    document = db.users.find()
    users_list = list(document)
    return users_list

# will take auth token and filter query over it 
def all_notes(current_user):
    doc = db.notes.find({"user_owner": current_user})
    notes_list = list(doc)
    print("All Users:", notes_list)
    return notes_list

# will take auth token and note's id and filter query over it mathcing the user auth inside the notes list
def notes_by_id(note_id):
    note = db.notes.find({"note_id" : str(note_id) })# find notes_by_id()
    print("your note" , list(note), type(note_id), note_id)
    return note

#  /api/search?q=:query: 
def notes_by_search_query():
    notes_list = db.notes.find()# search by keywords
    return notes_list
