from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO

from .config import configure_app, get_socketio_cors_origins
from .routes import bp
from .socket_events import register_socketio_handlers

load_dotenv()


def create_app():
    root_dir = Path(__file__).resolve().parent.parent
    template_folder = root_dir / "templates"
    static_folder = root_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(template_folder),
        static_folder=str(static_folder),
    )
    configure_app(app)
    app.register_blueprint(bp)
    return app


def create_socketio(app):
    cors_origins = get_socketio_cors_origins()
    socketio = SocketIO(app, cors_allowed_origins=cors_origins)
    register_socketio_handlers(socketio)
    return socketio


app = create_app()
socketio = create_socketio(app)
