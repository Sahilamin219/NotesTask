"""
Connect to MongoDB and initialize collections.

- `uri`: MongoDB connection string.
- `client`: MongoClient instance created by connecting to the MongoDB server using the provided connection string.
- `db`: MongoDB database instance named "timizli".
- `notes_collection`: MongoDB collection instance for storing notes, created within the "timizli" database.
- `user_collection`: MongoDB collection instance for storing user data, created within the "timizli" database.

This code snippet establishes a connection to MongoDB using the provided URI and initializes collections for notes and users.
"""


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