"""
This script:
    - Generates a token for every spice session
        - Token is a random string of 32 characters
        - Stores the token in a sqlite database
    - Can remove the token from the database at any time
"""

import sqlite3
import random
import string
import json

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
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.db_con[1].execute("INSERT INTO tokens VALUES (?, ?)", (token, port))
        self.db_con[0].commit()
        return token
    
    def remove_token(self, token):
        self.db_con[1].execute("DELETE FROM tokens WHERE token=?", (token,))
    
    def remove_token_all(self):
        self.db_con[1].execute("DELETE FROM tokens")
    
    def list_tokens(self):
        # return in json format
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
        return data

if __name__ == "__main__":
    tm = TokenManager()
    while True:
        print("1. Generate token")
        print("2. Remove token")
        print("3. List tokens")
        print("4. Remove all tokens")
        print("5. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            port = int(input("Enter port: "))
            tm.generate_token(port)
        elif choice == "2":
            token = input("Enter token: ")
            tm.remove_token(token)
        elif choice == "3":
            tokens = tm.list_tokens()
            print("Tokens:")
            print(json.dumps(tokens, indent=4))
        elif choice == "4":
            tm.remove_token_all()
        elif choice == "5":
            break
        else:
            print("Invalid choice")
        print("\n\n")
