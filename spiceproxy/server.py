import os
import socket
import json

# # Define the Unix socket file path
# SOCKET_PATH = "/tmp/unix_socket_example"

# # Remove the socket file if it already exists
# if os.path.exists(SOCKET_PATH):
#     os.remove(SOCKET_PATH)

# # Create a Unix socket
# server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# server_socket.bind(SOCKET_PATH)

# Define the host and port
HOST = '127.0.0.1'
PORT = 65432

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen(1)

# print(f"Server is listening on {SOCKET_PATH}")
print(f"Server is listening on {HOST}:{PORT}")

try:
    while True:
        conn, addr = server_socket.accept()
        print("Client connected")

        # Receive data from the client
        data = conn.recv(1024).decode("utf-8")
        if data:
            json_data = json.loads(data)
            print("Received JSON data:", json_data)

            # Prepare a response
            response = {"status": "success", "message": "Data received"}
            conn.send(json.dumps(response).encode("utf-8"))

        conn.close()
except KeyboardInterrupt:
    print("Server shutting down")
finally:
    server_socket.close()
    # os.remove(SOCKET_PATH)
