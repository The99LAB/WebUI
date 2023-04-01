## Diable cockpit
- ``systemctl disable --now cockpit.socket``

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

## Download VmManager
```
#!/usr/bin/env bash

# Authorize to GitHub to get the latest release tar.gz
# Requires: oauth token, https://help.github.com/articles/creating-an-access-token-for-command-line-use/
# Requires: jq package to parse json

# Your oauth token goes here, see link above
OAUTH_TOKEN="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"
# Repo owner (user id)
OWNER="macOS-KVM"
# Repo name
REPO="VmManager"
# The file name expected to download. This is deleted before curl pulls down a new one
FILE_NAME="VmManager-build.zip"

# Concatenate the values together for a
API_URL="https://$OAUTH_TOKEN:@api.github.com/repos/$OWNER/$REPO"

# Gets info on latest release, gets first uploaded asset id of a release,
# More info on jq being used to parse json: https://stedolan.github.io/jq/tutorial/
ASSET_ID=$(curl $API_URL/releases/latest | jq -r '.assets[0].id')
echo "Asset ID: $ASSET_ID"

# curl does not allow overwriting file from -O, nuke
rm -f $FILE_NAME

# curl:
# -O: Use name provided from endpoint
# -J: "Content Disposition" header, in this case "attachment"
# -L: Follow links, we actually get forwarded in this request
# -H "Accept: application/octet-stream": Tells api we want to dl the full binary
curl -O -J -L -H "Accept: application/octet-stream" "$API_URL/releases/assets/$ASSET_ID"
``` 


## Install python modules
- ``pip3 install -r requirements.txt``

## Disable firewall
- ``systemctl disable --now firewalld``

## Done
- Follow the instructions in the README.md file to run VmManager