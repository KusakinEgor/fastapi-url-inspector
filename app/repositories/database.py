import motor.motor_asyncio
from app.config import MONGO_URL, MONGO_DB_NAME

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]

links_collection = db["links"]
