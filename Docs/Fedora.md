# Install VMManager on Fedora Server

## Preparation
#### Diable cockpit
- ``systemctl disable --now cockpit.socket``
#### Install packages
```dnf install gcc python3-devel python3-pip qemu-kvm bridge-utils libvirt libvirt-devel dnf-plugins-core samba```
#### Disable firewall
- ``systemctl disable --now firewalld``
(It is recommended to keep the firewall enabled and configure it to allow the required ports)


## Libvirt
#### Enable libvirt
- ``systemctl enable --now libvirtd``
#### Create network bridge (networkManager)
- Create br0 bridge ``nmcli con add ifname br0 type bridge con-name br0``
- Find the name of the ethernet interface ``nmcli con show``. In this case it is ``enp37s0``
```nmcli con show
NAME     UUID                                  TYPE      DEVICE
br0      8a5dc2f8-2905-4614-832e-f3e46e24cae9  bridge    br0
enp37s0  761c8783-a96e-4285-9134-cee55dde94bd  ethernet  enp37s0
docker0  fe6fc3d4-f3f7-41f8-a633-215f43c2f392  bridge    docker0
virbr0   6dc5e5ee-48fb-4ea1-94e8-a049ac0bb523  bridge    virbr0
```
- Add bridge slave ``nmcli con add type bridge-slave ifname enp37s0 master br0``. Replace ``enp37s0`` with the name of the ethernet interface.
- Show the network configuration ``nmcli con show``
```nmcli con show
NAME                  UUID                                  TYPE      DEVICE
br0                   8a5dc2f8-2905-4614-832e-f3e46e24cae9  bridge    br0
enp37s0               761c8783-a96e-4285-9134-cee55dde94bd  ethernet  enp37s0
virbr0                6dc5e5ee-48fb-4ea1-94e8-a049ac0bb523  bridge    virbr0
bridge-slave-enp37s0  5f9b861e-b09c-4e08-b7e7-17171cb5f5fa  ethernet  --
```
- Disable the old connection ``nmcli con down enp37s0``. Replace ``enp37s0`` with the name of the ethernet interface. Note: this will disconnect your network connection.
- Enable the new connection ``nmcli con up br0``
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
( https://docs.docker.com/engine/install/fedora/ )
- ``dnf config-manager --add-repo=https://download.docker.com/linux/fedora/docker-ce.repo``
- ``dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin``
- ``systemctl start docker``
- ``systemctl enable docker``
#### Create macvlan network
- ``docker network create -d macvlan --subnet=$subnet --gateway= $gateway -o parent=br0 br0``


## Samba
- Copy the smb.conf file to ``/etc/samba/smb.conf``
- Create an empty samba-shares.conf file ```touch /etc/samba/samba-shares.conf```
- Enable samba: ``systemctl enable --now smb``


## VMManager Installation
#### Install custom blkinfo Python module
- Download from GitHub:
```
curl -s https://api.github.com/repos/macOS-KVM/blkinfo/releases/latest \
| grep "browser_download_url.*tar.gz" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -qi -
```
- Install the module: ``pip3 install blkinfo-*.tar.gz``

#### Download VmManager
- Download the latest release from GitHub:
```
curl -s https://api.github.com/repos/macOS-KVM/VmManager/releases/latest \
| grep "browser_download_url.*zip" \
| cut -d : -f 2,3 \
| tr -d \" \
| wget -qi -
```
- ``unzip VmManager-build.zip``
- ``cd VmManager-build``
#### Install python modules
- ``pip3 install -r requirements.txt``
#### Run VmManager
- Follow the instructions in the README.md file to run VmManager