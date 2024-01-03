from pymongo import MongoClient

uri = "mongodb+srv://dev:pass@cluster0.qndd2.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["db-dev"]

    
def user_via_id(user_id):
    return db.users.find_one({"user_id": user_id})
    

def all_users():
    document = db.users.find()
    return document
  