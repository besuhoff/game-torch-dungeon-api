from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
import httpx
from app.models.models import User
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
from fastapi.responses import RedirectResponse

router = APIRouter()
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    return user

callbackRoute = f"/auth/google/callback"

@router.get("/auth/google/url")
async def get_google_auth_url():
    state = secrets.token_urlsafe(32)
    url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.API_BASE_URL}{settings.API_PREFIX}{callbackRoute}&scope=openid%20email%20profile&state={state}"
    return {"url": url, "state": state}

@router.get(callbackRoute)
async def google_auth_callback(code: str, state: str):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.API_BASE_URL + settings.API_PREFIX + callbackRoute,
            },
        )
        token_data = token_response.json()
    
    # Verify token and get user info
    idinfo = id_token.verify_oauth2_token(
        token_data["id_token"],
        requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )
    
    # Find or create user
    user = await User.find_one({"google_id": idinfo["sub"]})
    if not user:
        user = User(
            email=idinfo["email"],
            google_id=idinfo["sub"],
            username=idinfo["email"].split("@")[0],  # Simple username from email
        )
        await user.insert()
    
    # Create access token
    access_token = await create_access_token({"sub": str(user.id)})
    
    # Redirect to game URL with token
    redirect_url = f"{settings.FRONTEND_URL}?token={access_token}"
    return RedirectResponse(url=redirect_url)

@router.get("/auth/user")
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user