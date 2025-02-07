import socket
import threading

# Proxy configuration
LISTEN_HOST = '0.0.0.0'  # Listen on all interfaces
LISTEN_PORT = 6000  # Port for the proxy to listen on

# Dictionary to store stop events for each port
stop_events = {}

def handle_client(client_socket):
    try:
        # Receive the HTTP CONNECT request
        request = client_socket.recv(4096).decode('utf-8')

        # Extract the target host and port from the CONNECT request
        if request.startswith('CONNECT'):
            print("Received request")
            print(f"Request: {request}")

            # Extract the host line from the request
            host_line = request.split('\n')[1].replace("Host: ", "").strip()
            """ Example host line:
            s99spiceproxy-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6:6000
            """
            print(f"Host line: {host_line}")
            # Check if the host line starts with "s99spiceproxy-"
            if host_line.startswith("s99spiceproxy-"):
                # Extract the token (between "s99spiceproxy-" and ":")
                token = host_line.split("-")[1].split(":")[0]
                print(f"Token: {token}")
                # Check if the token is valid
                target_host = "127.0.0.1"
                if token == "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6":
                    print("Token is valid")
                    target_port = 5900
                elif token == "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4":
                    print("Token is valid")
                    target_port = 5901
                else:
                    print("Token is invalid")
                    # Send back 401
                    client_socket.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')
                    return
            else:
                print("Invalid host line")
                # Send back 403
                client_socket.send(b'HTTP/1.1 403 Forbidden\r\n\r\n')
                return
            
            print(f"New target: {target_host}:{target_port}")

            # Connect to the target server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((target_host, target_port))

            # Send back a successful HTTP response
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            # Create a stop event for the target port if it doesn't exist
            if target_port not in stop_events:
                stop_events[target_port] = threading.Event()

            stop_event = stop_events[target_port]

            # Create two-way communication between the client and the target
            def forward_data(source, destination, stop_event):
                while not stop_event.is_set():
                    data = source.recv(4096)
                    if len(data) == 0:
                        break
                    destination.send(data)

            # Start two threads to forward data between client and server
            client_to_server = threading.Thread(target=forward_data, args=(client_socket, server_socket, stop_event))
            server_to_client = threading.Thread(target=forward_data, args=(server_socket, client_socket, stop_event))

            client_to_server.start()
            server_to_client.start()

            client_to_server.join()
            server_to_client.join()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        proxy_socket.bind((LISTEN_HOST, LISTEN_PORT))
    except socket.error as e:
        if e.errno == 98:  # Address already in use
            print(f"Port {LISTEN_PORT} is already in use. Please use a different port.")
            return
        else:
            raise

    proxy_socket.listen(5)
    print(f"SPICE Proxy listening on {LISTEN_HOST}:{LISTEN_PORT}...")

    try:
        while True:
            client_socket, _ = proxy_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("Shutting down proxy...")
        for event in stop_events.values():
            event.set()
    finally:
        proxy_socket.close()

if __name__ == "__main__":
    start_proxy()