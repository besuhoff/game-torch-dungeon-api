# Dungeon API

A multiplayer game API built with FastAPI and MongoDB, supporting real-time gameplay through WebSockets.

## Features

- Real-time multiplayer support via WebSockets
- Google OAuth2 authentication
- Game session management (create, join, leave)
- Game state persistence with MongoDB Atlas
- Save/Load game functionality
- Player state synchronization
- Flexible game world objects system

## Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Google OAuth2 credentials

## Setup

1. Clone the repository:
```bash
git clone [your-repo-url]
cd dungeon-api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
MONGODB_URL=your-mongodb-atlas-connection-string
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `/docs`.

## API Endpoints

### Authentication
- `GET /api/v1/auth/google/url` - Get Google OAuth2 URL
- `GET /api/v1/auth/google/callback` - Handle Google OAuth2 callback

### Game Sessions
- `POST /api/v1/sessions/create` - Create a new game session
- `GET /api/v1/sessions/list` - List active sessions
- `POST /api/v1/sessions/{session_id}/join` - Join a session
- `POST /api/v1/sessions/{session_id}/leave` - Leave a session

### Game Saves
- `POST /api/v1/saves/create` - Create a game save
- `GET /api/v1/saves/list` - List available saves
- `POST /api/v1/saves/{save_id}/load` - Load a game save

### WebSocket
- `WS /api/v1/ws/{session_id}` - Real-time game communication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
