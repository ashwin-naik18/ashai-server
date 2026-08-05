from pydantic import BaseModel

class userCreate(BaseModel):
    username : str
    email : str
    phone_no : str
    password : str


class userLogin(BaseModel):
    email : str
    password : str
    

