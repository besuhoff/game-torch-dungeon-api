from fastapi import APIRouter
from app.api.v1.endpoints import auth, sessions, websocket, saves, leaderboard

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(sessions.router, tags=["sessions"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(saves.router, tags=["saves"])
api_router.include_router(leaderboard.router, tags=["leaderboard"])
