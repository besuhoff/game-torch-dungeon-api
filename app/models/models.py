from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document, Link
from pydantic import EmailStr, Field
from enum import Enum

class PlayerRole(str, Enum):
    HOST = "host"
    PLAYER = "player"
    SPECTATOR = "spectator"

class PlayerState:
    position: Dict[str, float]  # {x: float, y: float}
    health: int = 100
    weapons: List[Dict[str, Any]] = []  # [{type: str, ammo: int}]
    effects: List[str] = []
    is_alive: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class WorldObject:
    type: str  # wall, enemy, bonus, etc
    x: float
    y: float
    properties: Optional[Dict[str, Any]] = None
    owner_id: Optional[str] = None  # For objects that belong to specific players

class User(Document):
    email: EmailStr
    google_id: str
    username: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_session: Optional[str] = None  # Reference to current GameSession

    class Settings:
        name = "users"
        indexes = [
            "email",
            "google_id",
            "current_session"
        ]

class GameSession(Document):
    name: str
    host: Link[User]
    players: Dict[str, PlayerState] = {}  # user_id: PlayerState
    max_players: int = 4
    is_private: bool = False
    password: Optional[str] = None
    world_map: List[WorldObject] = []
    shared_objects: List[WorldObject] = []  # Objects visible/interactive for all players
    game_state: Dict[str, Any] = {}  # Shared game state (scores, objectives, etc)
    player_roles: Dict[str, PlayerRole] = {}  # user_id: role
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "game_sessions"
        indexes = [
            "host",
            "is_active",
            "name"
        ]

class GameSave(Document):
    session: Link[GameSession]
    name: str
    description: Optional[str] = None
    players: Dict[str, PlayerState]  # Snapshot of all player states
    world_map: List[WorldObject]
    shared_objects: List[WorldObject]
    game_state: Dict[str, Any]
    created_by: Link[User]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "game_saves"
        indexes = [
            "session",
            "created_by"
        ]
