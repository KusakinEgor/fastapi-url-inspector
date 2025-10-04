import motor.motor_asyncio
from app.config import MONGO_URL, MONGO_DB_NAME

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB_NAME]

links_collection = mongo_db["links"]
