from .base import database, docker_client
from .images import Images
import json
from enum import Enum

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
    
    def create(self, name, type, webui, config):
        container_image = config['repository'] + ':' + config['tag']
        config_env = config['env']
        config_ports = config['ports']
        config_volumes = config['volumes']
        config_network = config['network']
        container_env = {}
        container_volumes = {}
        container_command = ""
        container_network_name = config_network['name']
        container_network_fixed_ip = None
        for env in config_env:
            container_env[env['name']] = env['value']
        for volume in config_volumes:
            # 'value' is the path on the host machine
            # 'bind' is the path inside the container
            container_volumes[volume['value']] = {'bind': volume['bind'], 'mode': volume['mode']}
        for command in config['command']:
            container_command += command['value'] + " "
        if 'ip' in config_network:
            container_network_fixed_ip = config_network['ip']
            container_network_config = self.docker_client.api.create_networking_config({
                container_network_name: self.docker_client.api.create_endpoint_config(
                    ipv4_address=container_network_fixed_ip
                )
            })
        else:
            container_network_config = self.docker_client.api.create_networking_config({
                container_network_name: self.docker_client.api.create_endpoint_config()
            })
    
        # Pull the image
        dockerImages = Images()
        dockerImages.pull(container_image, notify=False)

        # Create the container
        print(container_volumes) # container_volumes is a dictionary
        volumes_list = []
        for volume in config_volumes:
            volumes_list.append(volume['bind'])
        

        container = self.docker_client.api.create_container(
            image=container_image,
            name=name,
            environment=container_env,
            # volumes are the _container_volumes 
            # volumes list is from container_config['volumes']

            volumes=volumes_list,
            host_config=self.docker_client.api.create_host_config(binds=container_volumes),
            networking_config=container_network_config,
            command=container_command,
            detach=True,
            tty=True,
            stdin_open=True,
        )

        # Add the container to the database
        self.db_cursor.execute('INSERT INTO docker_containers (id, container_type, webui, config) VALUES (?, ?, ?, ?)', 
            (container['Id'], type, json.dumps(webui), json.dumps(config)))        
        self.db_conn.commit()

        # Return the container id
        return container['Id']

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
    