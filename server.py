from flask import Flask
from flask_socketio import SocketIO
from config import Config
from routes import init_routes

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=Config.SOCKETIO_CORS_ALLOWED_ORIGINS,
        async_mode=Config.SOCKETIO_ASYNC_MODE
    )
    
    # Initialize routes
    init_routes(app, socketio)
    
    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    
    print(f"Starting RFID Log Server on {Config.HOST}:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    
    socketio.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT, 
        debug=Config.DEBUG, 
        allow_unsafe_werkzeug=True
    )

