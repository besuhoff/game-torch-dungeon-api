from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.models import User, GameSession, GameSave
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/saves/create")
async def create_save(
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if not current_user.current_session:
        raise HTTPException(
            status_code=400,
            detail="User is not in any active session"
        )
    
    session = await GameSession.get(current_user.current_session)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create save from current session state
    save = GameSave(
        session=session,
        name=name,
        description=description,
        players=session.players.copy(),
        world_map=session.world_map.copy(),
        shared_objects=session.shared_objects.copy(),
        game_state=session.game_state.copy(),
        created_by=current_user
    )
    await save.insert()
    
    return save

@router.get("/saves/list")
async def list_saves(
    current_user: User = Depends(get_current_user)
) -> List[GameSave]:
    return await GameSave.find(
        {"created_by": current_user.id}
    ).to_list()

@router.post("/saves/{save_id}/load")
async def load_save(
    save_id: str,
    current_user: User = Depends(get_current_user)
):
    save = await GameSave.get(save_id)
    if not save:
        raise HTTPException(status_code=404, detail="Save not found")
    
    # Create new session from save
    session = GameSession(
        name=f"{save.name} (Loaded)",
        host=current_user,
        players={str(current_user.id): save.players[str(save.created_by.id)]},
        world_map=save.world_map,
        shared_objects=save.shared_objects,
        game_state=save.game_state,
        player_roles={str(current_user.id): PlayerRole.HOST}
    )
    await session.insert()
    
    # Update user's current session
    current_user.current_session = str(session.id)
    await current_user.save()
    
    return session
