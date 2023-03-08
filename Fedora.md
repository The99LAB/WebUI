## Install packages
- gcc
- python3-devel
- python3-pip
- qemu-kvm
- bridge-utils
- libvirt
- libvirt-devel

## Enable libvirt
- ``systemctl enable --now libvirtd``

## Create network bridge (networkManager)
- Create br0 bridge ``nmcli con add ifname br0 type bridge con-name br0``
- Add bridge slave ``nmcli con add type bridge-slave ifname eno1 master br0``
- Show the network configuration ``nmcli con show``
```nmcli con show
NAME                  UUID                                  TYPE      DEVICE
br0                   aa0793c2-f9cd-4f03-9e38-9ee0c75fd47a  bridge    br0
bridge-slave-enp37s0  d437f2a7-c20b-4902-88f8-945bd2753274  ethernet  enp37s0
eno1               482c2e29-dfcc-482e-84e3-3d5ca2f8519c  ethernet  --
```
- Disable the old connection ``nmcli con down eno1``
- Enable the new connection ``nmcli con up br0``
- Show the ip settings ``ip a s`` (``br0`` should have an ip address) 
Note: connecting may take some time

## Add network bridge to libvirt
- ``nano /tmp/br0.xml``
``` 
<network>
  <name>br0</name>
  <forward mode='bridge'/>
  <bridge name='br0'/>
</network>
```
- ``virsh net-define /tmp/br0.xml``
- ``virsh net-start br0``
- ``virsh net-autostart br0``

## Install python modules
- ``pip3 install -r requirements.txt``

## Start VmManager
- ``python3 VmManager.py``
