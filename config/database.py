from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Constants from .env
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client["Advaita2025"]
    users_collection = db["users"]
    tickets_collection = db["tickets"]
except Exception as e:
    print(e)
