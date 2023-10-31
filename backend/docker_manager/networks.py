from .base import docker_client

class Networks:
    def __init__(self):
        self.docker_client = docker_client()
    
    def getAll(self):
        api_networks = self.docker_client.networks.list()
        networks_list = []
        for network in api_networks:
            network_id = network.short_id
            network_name = network.name
            network_driver = network.attrs["Driver"]
            network_scope = network.attrs["Scope"]
            # Only macvlan and ipvlan networks can have containers with static IPs
            network_custom_ip = False
            network_subnet = ""
            if network_driver == "macvlan" or network_driver == "ipvlan":
                network_custom_ip = True
            # check if network has subnet
            if 'Config' in network.attrs['IPAM'] and len(network.attrs['IPAM']['Config']) > 0 and 'Subnet' in network.attrs['IPAM']['Config'][0]:
                network_subnet = network.attrs['IPAM']['Config'][0]['Subnet']
            
            networks_list.append({
                "id": network_id,
                "name": network_name,
                "driver": network_driver,
                "scope": network_scope,
                "custom_ip": network_custom_ip,
                "subnet": network_subnet,
            })
        return networks_list
    
    def delete(self, id):
        network = self.docker_client.networks.get(id)
        network.remove()