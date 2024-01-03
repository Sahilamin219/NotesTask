from pydantic import BaseModel
class User(BaseModel):
    pass

class UserInput(BaseModel):
    username: str
    password: str

class NotesInput(BaseModel):
    notes_content: str

class UserName(BaseModel):
    username : str