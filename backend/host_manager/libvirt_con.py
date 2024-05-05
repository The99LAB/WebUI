import libvirt
from .hostManagerException import HostManagerException


# Create a connection to libvirt
# When this module is imported, a connection to libvirt is created
# this connection is stored globally and is used by other modules
# so do not create multiple connections to libvirt
# this means that the connection should be global and should be created only once

class LibvirtConnection:
    def __init__(self):
        print('INIT LIBVIRT CONNECTION')
        self.libvirt_conn = libvirt.open("qemu:///system")
    
    @property
    def connection(self):
        return self.libvirt_conn
    
libvirt_connection = LibvirtConnection()