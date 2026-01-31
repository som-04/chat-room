from flask import request, session
from flask_socketio import emit, join_room, leave_room, send

from .state import rooms


def register_socketio_handlers(socketio):
    @socketio.on("message")
    def message(data):
        room = session.get("room")
        if room not in rooms:
            return
        content = {"name": session.get("name"), "message": data["data"]}
        send(content, to=room)
        rooms[room]["messages"].append(content)
        print(f"{session.get('name')} said: {data['data']}")

    @socketio.on("connect")
    def connect(auth):
        room = session.get("room")
        name = session.get("name")
        if not room or not name:
            return
        if room not in rooms:
            leave_room(room)
            return

        join_room(room)
        send({"name": name, "message": "has entered the room"}, to=room)
        rooms[room]["members"] += 1
        rooms[room].setdefault("peers", {})
        print(f"{name} joined the room {room}")

    @socketio.on("disconnect")
    def disconnect():
        room = session.get("room")
        name = session.get("name")
        leave_room(room)
        if room in rooms:
            rooms[room]["members"] -= 1
            peers = rooms[room].get("peers", {})
            if request.sid in peers:
                del peers[request.sid]
                emit("voice_peer_left", {"id": request.sid}, to=room)
            if rooms[room]["members"] <= 0:
                del rooms[room]

        send({"name": name, "message": "has left the room"}, to=room)
        print(f"{name} left the room {room}")

    @socketio.on("voice_join")
    def voice_join():
        room = session.get("room")
        name = session.get("name")
        if not room or room not in rooms:
            return

        peers = rooms[room].setdefault("peers", {})
        peers[request.sid] = name

        existing_peers = [
            {"id": peer_id, "name": peer_name}
            for peer_id, peer_name in peers.items()
            if peer_id != request.sid
        ]
        emit("voice_peers", {"peers": existing_peers})
        emit(
            "voice_peer_joined",
            {"id": request.sid, "name": name},
            to=room,
            include_self=False,
        )

    @socketio.on("voice_leave")
    def voice_leave():
        room = session.get("room")
        if not room or room not in rooms:
            return
        peers = rooms[room].get("peers", {})
        if request.sid in peers:
            del peers[request.sid]
            emit("voice_peer_left", {"id": request.sid}, to=room)

    @socketio.on("voice_signal")
    def voice_signal(data):
        room = session.get("room")
        if not room or room not in rooms:
            return
        target_id = data.get("to")
        if not target_id:
            return
        payload = {
            "from": request.sid,
            "description": data.get("description"),
            "candidate": data.get("candidate"),
        }
        emit("voice_signal", payload, to=target_id)
