import json
import socket

message = json.dumps({
    "type": "get_viewport_screenshot",
    "params": {
        "filepath": r"C:\Users\yhsn5\Downloads\NASASPACEAPP\previews\base_rocks.png",
        "max_size": 1280,
    },
}) + "\n"
with socket.create_connection(("127.0.0.1", 9875), timeout=40) as sock:
    sock.sendall(message.encode("utf-8"))
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(65536)
        if not chunk:
            break
        data += chunk
print(data.decode("utf-8", errors="replace")[:1500])
