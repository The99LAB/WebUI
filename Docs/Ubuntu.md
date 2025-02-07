# Install the WebUI on Ubuntu Server 24.04 LTS

## Preparation
#### Install packages
```apt install -y python3-pip bridge-utils cpu-checker libvirt-clients libvirt-daemon-system libvirt-daemon libvirt-dev qemu-kvm samba ```

<!---
#### Disable firewall
- ``systemctl disable --now ufw``
(It is recommended to keep the firewall enabled and configure it to allow the required ports)
--->


## Libvirt
<!---
#### Enable libvirt
- ``systemctl enable --now libvirtd``
#### Create network bridge (networkManager)
TODO: Explain how to do this on ubuntu
- Refresh the dhcp lease ``dhclient -r br0`` and ``dhclient br0``
- Show the ip settings ``ip a s`` (``br0`` should have an ip address) 
#### Add network bridge to libvirt
- Create ``tmp/br0.xml`` with the following content:
``` 
<network>
  <name>br0</name>
  <forward mode='bridge'/>
  <bridge name='br0'/>
</network>
```
- ``virsh net-define /tmp/br0.xml``
- Start the network: ``virsh net-start br0``
- Autostart the network: ``virsh net-autostart br0``

## Docker
#### Installation
( https://docs.docker.com/engine/install/ubuntu/ )
--->


## Samba
- Copy the smb.conf file to ``/etc/samba/smb.conf``
- Create an empty samba-shares.conf file ```touch /etc/samba/samba-shares.conf```
- Enable samba: ``systemctl enable --now smb``


## WebUI Installation

#### Download the WebUI
- Download the latest release from GitHub:
```
curl -s https://api.github.com/repos/99-industries/WebUI/releases/latest \
| grep "browser_download_url.*zip" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -qi -
```
- ``unzip WebUI-build.zip``
- ``cd WebUI-build``
#### Install python modules
- ``pip3 install -r requirements.txt``
#### Run the WebUI
- Follow the instructions in the README.md file to run the WebUI