from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.models import User, GameSave

async def init_db():
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the MongoDB client and document models
    await init_beanie(
        database=client.get_default_database(),
        document_models=[
            User,
            GameSave
        ]
    )
