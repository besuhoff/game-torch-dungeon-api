from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set
import json
from app.models.models import User, GameSession, PlayerState
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        # session_id -> {user_id -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][user_id] = websocket
        
    def disconnect(self, session_id: str, user_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].pop(user_id, None)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                
    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: str = None):
        if session_id in self.active_connections:
            for user_id, connection in self.active_connections[session_id].items():
                if user_id != exclude_user:
                    await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str
):
    try:
        # Authenticate user
        user = await get_current_user(token)
        if not user or user.current_session != session_id:
            await websocket.close(code=4001)
            return
            
        session = await GameSession.get(session_id)
        if not session or not session.is_active:
            await websocket.close(code=4002)
            return
            
        # Connect to WebSocket
        await manager.connect(websocket, session_id, str(user.id))
        
        # Notify others that user has connected
        await manager.broadcast_to_session(
            session_id,
            {
                "type": "user_connected",
                "user_id": str(user.id),
                "username": user.username
            },
            exclude_user=str(user.id)
        )
        
        try:
            while True:
                data = await websocket.receive_json()
                
                # Handle different message types
                if data["type"] == "position_update":
                    # Update player position
                    session.players[str(user.id)].position = data["position"]
                    session.players[str(user.id)].last_updated = datetime.utcnow()
                    await session.save()
                    
                    # Broadcast to other players
                    await manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "position_update",
                            "user_id": str(user.id),
                            "position": data["position"]
                        },
                        exclude_user=str(user.id)
                    )
                    
                elif data["type"] == "game_action":
                    # Handle game actions (shooting, item pickup, etc.)
                    action_type = data["action"]
                    if action_type == "shoot":
                        # Process shooting logic
                        target_hit = data.get("target_hit")
                        if target_hit:
                            target_id = target_hit["user_id"]
                            damage = target_hit["damage"]
                            if target_id in session.players:
                                session.players[target_id].health -= damage
                                if session.players[target_id].health <= 0:
                                    session.players[target_id].is_alive = False
                                await session.save()
                    
                    # Broadcast action to other players
                    await manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "game_action",
                            "user_id": str(user.id),
                            "action": data
                        },
                        exclude_user=str(user.id)
                    )
                    
        except WebSocketDisconnect:
            manager.disconnect(session_id, str(user.id))
            await manager.broadcast_to_session(
                session_id,
                {
                    "type": "user_disconnected",
                    "user_id": str(user.id),
                    "username": user.username
                }
            )
            
    except Exception as e:
        await websocket.close(code=4000)
        return
