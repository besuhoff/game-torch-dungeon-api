from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.models import User, GameSession, GameSave

async def init_db():
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the MongoDB client and document models
    await init_beanie(
        database=client.dungeon_api,  # Specify the database name explicitly
        document_models=[
            User,
            GameSession,
            GameSave
        ]
    )
