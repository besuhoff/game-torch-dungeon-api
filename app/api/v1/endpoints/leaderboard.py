from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.models import User, GameSave
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

def calculate_score(save: GameSave) -> int:
    player_state = save.players.get(str(save.created_by.id))
    if not player_state:
        return 0
        
    score = 0
    # Base score from health
    score += player_state.health
    # Points for weapons
    score += len(player_state.weapons) * 50
    # Points for being alive
    if player_state.is_alive:
        score += 100
    
    return score

@router.get("/leaderboard/global")
async def get_global_leaderboard(
    limit: Optional[int] = 10,
    timeframe: Optional[str] = "all"  # all, weekly, monthly
) -> List[dict]:
    query = {}
    
    if timeframe == "weekly":
        week_ago = datetime.now(datetime.timezone.utc) - timedelta(days=7)
        query["created_at"] = {"$gte": week_ago}
    elif timeframe == "monthly":
        month_ago = datetime.now(datetime.timezone.utc) - timedelta(days=30)
        query["created_at"] = {"$gte": month_ago}
        
    saves = await GameSave.find(query).to_list()
    
    # Calculate scores for each save
    scored_saves = [
        {
            "username": save.created_by.username,
            "score": calculate_score(save),
            "save_name": save.name,
            "created_at": save.created_at
        }
        for save in saves
    ]
    
    # Sort by score and limit
    return sorted(scored_saves, key=lambda x: x["score"], reverse=True)[:limit]

@router.get("/leaderboard/user/{user_id}")
async def get_user_stats(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    saves = await GameSave.find(
        {"created_by": user_id}
    ).to_list()
    
    if not saves:
        return {
            "total_games": 0,
            "highest_score": 0,
            "average_score": 0,
            "recent_scores": []
        }
    
    scores = [calculate_score(save) for save in saves]
    total_games = len(scores)
    highest_score = max(scores) if scores else 0
    average_score = sum(scores) / total_games if scores else 0
    
    # Get 5 most recent scores
    recent_saves = sorted(saves, key=lambda x: x.created_at, reverse=True)[:5]
    recent_scores = [
        {
            "save_name": save.name,
            "score": calculate_score(save),
            "created_at": save.created_at
        }
        for save in recent_saves
    ]
    
    return {
        "total_games": total_games,
        "highest_score": highest_score,
        "average_score": average_score,
        "recent_scores": recent_scores
    }
