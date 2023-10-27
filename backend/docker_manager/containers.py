from .base import database

class Containers:
    def __init__(self):
        self.db_conn = database()
        self.db_cursor = self.db_conn.cursor()
    
    def getAll(self):
        return self.db_cursor.execute('SELECT * FROM docker_containers').fetchall()

    def get(self, id):
        return self.db_cursor.execute('SELECT * FROM docker_containers WHERE id = ?', (id,)).fetchone()
    
    def delete(self, id):
        self.db_cursor.execute('DELETE FROM docker_containers WHERE id = ?', (id,))
        self.db_conn.commit()
    