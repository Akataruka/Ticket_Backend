from pydantic import BaseModel, Field

# User Model
class User(BaseModel):
    name: str = Field(..., example="john_doe")
    password: str = Field(..., example="strongpassword")
    role: str = Field(..., example="validator")
