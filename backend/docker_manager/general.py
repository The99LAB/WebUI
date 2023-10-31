from .base import docker_client

class General:
    def __init__(self):
        self.docker_client = docker_client()
    
    def version(self):
        return self.docker_client.version()