import socket
import threading
import json
import sqlite3
import random
import string

class SpiceProxy:
    def __init__(self):
        self.LISTEN_HOST = '0.0.0.0'
        self.LISTEN_PORT = 6000
        self.target_host = '127.0.0.1'
        self.stop_events = {}
        self.proxy_stop_event = threading.Event()
        self.handle_client_stop_event = threading.Event()
        self.proxy_map = []

    def handle_client(self, client_socket):
        try:
            request = client_socket.recv(4096).decode('utf-8')
            if request.startswith('CONNECT'):
                host_line = request.split('\n')[1].replace("Host: ", "").strip()
                if host_line.startswith("s99spiceproxy-"):
                    token = host_line.split("-")[1].split(":")[0]
                    target_port = None
                    for proxy in self.proxy_map:
                        if proxy["token"] == token:
                            target_port = proxy["port"]
                            break
                    if target_port is None:
                        client_socket.send(b'HTTP/1.1 401 Unauthorized\r\n\r\n')
                        return
                else:
                    client_socket.send(b'HTTP/1.1 403 Forbidden\r\n\r\n')
                    return
                
                print(f"New target: {self.target_host}:{target_port}")
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((self.target_host, target_port))
                client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                if token not in self.stop_events:
                    self.stop_events[token] = threading.Event()
                stop_event = self.stop_events[token]
                def forward_data(source, destination, stop_event):
                    while not stop_event.is_set():
                        data = source.recv(4096)
                        if len(data) == 0:
                            break
                        destination.send(data)
                client_to_server = threading.Thread(target=forward_data, args=(client_socket, server_socket, stop_event))
                server_to_client = threading.Thread(target=forward_data, args=(server_socket, client_socket, stop_event))
                client_to_server.start()
                server_to_client.start()
                client_to_server.join()
                server_to_client.join()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Closing client socket")
            client_socket.close()

    def start_proxy(self):
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            proxy_socket.bind((self.LISTEN_HOST, self.LISTEN_PORT))
        except socket.error as e:
            if e.errno == 98:
                print(f"Port {self.LISTEN_PORT} is already in use. Please use a different port.")
                return
            else:
                raise
        proxy_socket.listen(5)
        proxy_socket.settimeout(1)
        print(f"SPICE Proxy listening on {self.LISTEN_HOST}:{self.LISTEN_PORT}...")
        while not self.proxy_stop_event.is_set():
            try:
                client_socket, _ = proxy_socket.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
            except socket.timeout:
                continue

        proxy_socket.close()

    def stop_proxy_for_token(self, token):
        if token in self.stop_events:
            self.stop_events[token].set()
            print(f"Stopped proxy for token {token}")
        else:
            print(f"No proxy running for token {token}")

    def stop_all_proxies(self):
        for event in self.stop_events.values():
            event.set()
        print("Stopped all proxies")

    def stop_proxy(self):
        self.proxy_stop_event.set()

    def main(self):
        proxy_thread = threading.Thread(target=self.start_proxy)
        proxy_thread.start()

class TokenManager:
    def __init__(self):
        conn = sqlite3.connect("tokens.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tokens (token TEXT, port INTEGER)")
        self.db_con = conn, c
    
    def __del__(self):
        self.db_con[0].close()

    def db_close(self, conn):
        self.db_con[0].close()
        self.db_con = None

    def generate_token(self, port: int):
        if not isinstance(port, int):
            return None
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.db_con[1].execute("INSERT INTO tokens VALUES (?, ?)", (token, port))
        self.db_con[0].commit()
        return token
    
    def remove_token(self, token):
        self.db_con[1].execute("DELETE FROM tokens WHERE token=?", (token,))
        self.db_con[0].commit()
    
    def remove_token_all(self):
        self.db_con[1].execute("DELETE FROM tokens")
        self.db_con[0].commit()
    
    def list_tokens(self):
        """
        [
            {
                "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "port": 5900
            }
        ]
        """
        self.db_con[1].execute("SELECT * FROM tokens")
        data = self.db_con[1].fetchall()
        for i in range(len(data)):
            data[i] = {"token": data[i][0], "port": data[i][1]}
        return data

if __name__ == "__main__":
    token_manager = TokenManager()
    token_manager.remove_token_all()
    proxy = SpiceProxy()
    proxy.proxy_map = token_manager.list_tokens()
    proxy.main()
    print(f"Proxy map: {proxy.proxy_map}")
    try:
        while True:
            print("1. Generate token")
            print("2. Remove token")
            print("3. List tokens")
            print("4. Remove all tokens")
            print("5. Exit")
            
            choice = input("Enter choice: ")
            if choice == "1":
                port = int(input("Enter port: "))
                token = token_manager.generate_token(port)
                if token is not None:
                    print(f"Generated token: {token} for port {port}")
            
            elif choice == "2":
                token = input("Enter token: ")
                token_manager.remove_token(token)
                proxy.stop_proxy_for_token(token)
            
            elif choice == "3":
                tokens = token_manager.list_tokens()
                print("Tokens:")
                print(json.dumps(tokens, indent=4))

            elif choice == "4":
                token_manager.remove_token_all()
                proxy.stop_all_proxies()
            
            elif choice == "5":
                break
            
            else:
                print("Invalid choice")


            proxy.proxy_map = token_manager.list_tokens()
            print("\n\n")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        print("Cleaning up...")
        proxy.stop_all_proxies()
        proxy.stop_proxy()
        del proxy
        del token_manager
