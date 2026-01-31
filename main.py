from app import app, socketio
from app.config import get_runtime_options


if __name__ == "__main__":
    host, port, debug_flag = get_runtime_options(app)
    socketio.run(app, host=host, port=port, debug=debug_flag)
