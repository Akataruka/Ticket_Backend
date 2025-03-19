from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.mongo_client import MongoClient
from models.ticket import Ticket
from models.user import User
from bson import ObjectId
from passlib.context import CryptContext
import jwt
import datetime
from typing import Optional
from pydantic import BaseModel, Field
import os




# Constants from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
MONGO_URL = os.getenv("MONGO_URL")


client = MongoClient(MONGO_URL)

db = client["Advaita2025"]
users_collection = db["users"]
tickets_collection = db["tickets"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# FastAPI App
app = FastAPI()


# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    return users_collection.find_one({"name": username})

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user and verify_password(password, user["password"]):
        return user
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
def home():
    return "welcome to advaita ticket backend"
    
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["name"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer","role":user["role"]}

@app.post("/validator/add_code")
def add_code(ticket: Ticket, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "validator":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    if tickets_collection.find_one({"code": ticket.code}):
        return {"message": "Duplicate code"}
    tickets_collection.insert_one(ticket.dict())
    return {"message": "Code added successfully"}

@app.post("/authenticator/validate_code")
def validate_code(code: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "authenticator":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    ticket = tickets_collection.find_one({"code": code})
    if not ticket:
        return {"message": "Invalid code"}
    if ticket["validated_status"]:
        return {"message": "Code already validated before"}
    tickets_collection.update_one({"_id": ticket["_id"]}, {"$set": {"validated_status": True}})
    return {"message": "Code validated successfully"}
