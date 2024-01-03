from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["db-dev"]



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

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/users")
def users():
    from fetcher import all_users
    x =  all_users()
    return json.loads(json.dumps({"content": list(x)}, default=str))


from pydantic import BaseModel

class UserProgressForm(BaseModel):
    user_email: str
    password: str


@app.post("/register")
def read_item(item: UserProgressForm ):
    user_email = item.user_email
    password = item.password
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)