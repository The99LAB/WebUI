from .base import database, docker_client
import json

class Containers:
    def __init__(self):
        self.db_conn = database()
        self.db_cursor = self.db_conn.cursor()
        self.docker_client = docker_client()
    
    def getAll(self):
        api_containers = self.docker_client.containers.list(all=True)
        docker_containers = []
        for container in api_containers:
            api_id = container.id
            docker_containers.append(self.get(api_id))
        return docker_containers

    def get(self, id):
        _container = self.docker_client.containers.get(id)
        _container_status = _container.status
        _container_name = _container.name
        # If the container does not exist in the database, mark the container as unmanaged.
        self.db_cursor.execute('SELECT * FROM docker_containers WHERE id = ?', (id,))
        row = self.db_cursor.fetchone()
        container_type = 'unmanaged'
        container_webui = ''
        container_config = ''
        if row:
            container_type = row['container_type']
            container_webui = json.loads(row['webui'])
            container_config = json.loads(row['config'])

        container_dhcp_ip = None
        if _container_status == "running":
            try:
                container_dhcp_ip = _container.attrs["NetworkSettings"]["Networks"][list(_container.attrs["NetworkSettings"]["Networks"].keys())[0]]["IPAddress"]
                if container_dhcp_ip == '':
                        container_dhcp_ip = None
                if container_config.get("network"):
                    container_config["network"]["dhcp_ip"] = container_dhcp_ip
            except KeyError:
                pass

        return {
            "id": id,
            "container_type": container_type,
            "status": _container_status,
            "name": _container_name,
            "webui": container_webui,
            "config": container_config,
        }
    
    def create(self, name, type, config, webui, command):
        return
    
    def delete(self, id, api_only=False):
        container = self.docker_client.containers.get(id)
        container.remove()
        if not api_only:
            self.db_cursor.execute('DELETE FROM docker_containers WHERE id = ?', (id,))
            self.db_conn.commit()

    def start(self, id):
        container = self.docker_client.containers.get(id)
        container.start()
    
    def stop(self, id):
        container = self.docker_client.containers.get(id)
        container.stop()
    
    def restart(self, id):
        container = self.docker_client.containers.get(id)
        container.restart()
    