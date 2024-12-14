from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.models import User, GameSession, PlayerRole, PlayerState
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/sessions/create")
async def create_session(
    name: str,
    max_players: int = 4,
    is_private: bool = False,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    session = GameSession(
        name=name,
        host=current_user,
        max_players=max_players,
        is_private=is_private,
        password=password,
        player_roles={str(current_user.id): PlayerRole.HOST},
        players={
            str(current_user.id): PlayerState(
                position={"x": 0, "y": 0},
                health=100,
                weapons=[],
                effects=[]
            )
        }
    )
    await session.insert()
    
    # Update user's current session
    current_user.current_session = str(session.id)
    await current_user.save()
    
    return session

@router.get("/sessions/list")
async def list_sessions(
    current_user: User = Depends(get_current_user)
) -> List[GameSession]:
    return await GameSession.find(
        {"is_active": True}
    ).to_list()

@router.post("/sessions/{session_id}/join")
async def join_session(
    session_id: str,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    session = await GameSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if len(session.players) >= session.max_players:
        raise HTTPException(status_code=400, detail="Session is full")
    
    if session.is_private and session.password != password:
        raise HTTPException(status_code=403, detail="Invalid password")
    
    # Add player to session
    session.players[str(current_user.id)] = PlayerState(
        position={"x": 0, "y": 0},
        health=100,
        weapons=[],
        effects=[]
    )
    session.player_roles[str(current_user.id)] = PlayerRole.PLAYER
    await session.save()
    
    # Update user's current session
    current_user.current_session = str(session.id)
    await current_user.save()
    
    return session

@router.post("/sessions/{session_id}/leave")
async def leave_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    session = await GameSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Remove player from session
    if str(current_user.id) in session.players:
        del session.players[str(current_user.id)]
        del session.player_roles[str(current_user.id)]
        
        # If host leaves, assign new host or close session
        if str(current_user.id) == str(session.host.id):
            if session.players:
                new_host_id = next(iter(session.players))
                session.host = await User.get(new_host_id)
                session.player_roles[new_host_id] = PlayerRole.HOST
            else:
                session.is_active = False
        
        await session.save()
    
    # Clear user's current session
    current_user.current_session = None
    await current_user.save()
    
    return {"message": "Successfully left session"}
