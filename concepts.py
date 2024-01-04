from pydantic import BaseModel
class User(BaseModel):
    """
    Pydantic model for representing a user.
    No fields are defined in this model.

    Example Usage:
    ```
    user_instance = User()
    ```

    Note: This model does not enforce any specific fields.

    """
    pass

class UserInput(BaseModel):
    """
    Pydantic model for representing user input during user registration or authentication.

    Attributes:
    - `username` (str): The username of the user.
    - `password` (str): The password of the user.

    Example Usage:
    ```
    user_input_instance = UserInput(username="example_user", password="example_password")
    ```

    """
    username: str
    password: str

class NotesInput(BaseModel):
    """
    Pydantic model for representing input data when creating a new note.

    Attributes:
    - `notes_content` (str): The content of the note.

    Example Usage:
    ```
    notes_input_instance = NotesInput(notes_content="This is a new note.")
    ```

    """
    notes_content: str

class UserName(BaseModel):
    """
    Pydantic model for representing a username.

    Attributes:
    - `username` (str): The username.

    Example Usage:
    ```
    username_instance = UserName(username="example_user")
    ```

    """
    username : str