from pymongo import MongoClient

uri = "mongodb+srv://dev:QNqJI6RLuKINK5Ln@cluster0.lt9o4td.mongodb.net/timizli?retryWrites=true&w=majority"
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
user_collection = db["users"]