import os
import socket
import json
import threading

# # Define the Unix socket file path
# SOCKET_PATH = "/tmp/unix_socket_example"

# # Remove the socket file if it already exists
# if os.path.exists(SOCKET_PATH):
#     os.remove(SOCKET_PATH)

HOST = '127.0.0.1'
PORT = 65432

# Function to handle individual client connections
def handle_client(conn):
    try:
        # Receive data from the client
        data = conn.recv(1024).decode("utf-8")
        if data:
            json_data = json.loads(data)
            print(f"Received from client: {json_data}")

            # Prepare and send a response
            response = {"status": "success", "message": "Data received"}
            conn.send(json.dumps(response).encode("utf-8"))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()
        print("Client disconnected")

# Create a Unix socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)  # Allow up to 5 clients in the queue
server_socket.settimeout(5)

# print(f"Server is listening on {SOCKET_PATH}")
print(f"Server is listening on {HOST}:{PORT}")


try:
    while True:
        try:
            conn, _ = server_socket.accept()
            print("Client connected")

            # Handle the client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()
        except socket.timeout:
            continue

except KeyboardInterrupt:
    print("Server shutting down")
finally:
    server_socket.close()
    # os.remove(SOCKET_PATH)
