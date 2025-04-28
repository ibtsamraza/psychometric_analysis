import socketio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("socketio")

# Set up Socket.IO with debug enabled
sio = socketio.AsyncServer(
    async_mode='asgi', 
    cors_allowed_origins=["*"],
    logger=logger,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e8,
    allow_upgrades=True
)
socket_app = socketio.ASGIApp(sio)

# Add a connection event handler
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    print(f"Connection details: {environ.get('HTTP_USER_AGENT', 'Unknown')}")
    
    # Send a welcome message to confirm connection
    await sio.emit('welcome', {'message': 'Connected to server'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Helper function to emit agent updates
async def emit_agent_update(session_id, agent, status, progress):
    if session_id:
        print(f"Emitting agent update: {agent} - {status} - {progress}% for session {session_id}")
        try:
            await sio.emit('agent_update', {
                'session_id': session_id,
                'agent': agent,
                'status': status,
                'progress': progress
            })
            print(f"Emit completed for {agent}")
        except Exception as e:
            print(f"Error emitting agent update: {e}") 