import socket
import json

# # Define the Unix socket file path
# SOCKET_PATH = "/tmp/unix_socket_example"

# # Create a Unix socket
# client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# Define the host and port
HOST = '127.0.0.1'
PORT = 65432

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    # client_socket.connect(SOCKET_PATH)
    client_socket.connect((HOST, PORT))
    print("Connected to server")
    
    print("Select action:")
    print("1. List tokens")
    print("2. Generate token")
    print("3. Remove token")
    print("4. Remove all tokens")
    print("5. Exit")

    choice = input("Enter choice: ")
    if choice == "1":
        data_to_send = {"action": "list_tokens"}
    elif choice == "2":
        port = int(input("Enter port: "))
        data_to_send = {"action": "generate_token", "port": port}
    elif choice == "3":
        token = input("Enter token: ")
        data_to_send = {"action": "remove_token", "token": token}
    elif choice == "4":
        data_to_send = {"action": "remove_token_all"}
    elif choice == "5":
        exit()

    client_socket.send(json.dumps(data_to_send).encode("utf-8"))

    # Receive the response from the server
    response = client_socket.recv(1024).decode("utf-8")
    if response:
        json_response = json.loads(response)
        print("Received response:")
        print(json.dumps(json_response, indent=4))

finally:
    client_socket.close()
