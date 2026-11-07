import json
import socket

message = json.dumps({
    "type": "save_as_mainfile",
    "params": {"filepath": r"C:\Users\yhsn5\Downloads\NASASPACEAPP\MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend"},
}) + "\n"
with socket.create_connection(("127.0.0.1", 9875), timeout=120) as sock:
    sock.sendall(message.encode("utf-8"))
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(65536)
        if not chunk:
            break
        data += chunk
print(data.decode("utf-8", errors="replace")[:1500])
