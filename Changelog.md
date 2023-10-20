# Changelog
### 1.0
- initial release

### 1.1
- Settings: Remove/Add OVMF Paths
- Tools: System Information: Fix incorrect memory size
- Frontend: Add dark mode
- Login Page: redesign
- Add terminal
- CreateVM: Add Windows 11 support
- Change page title when switching pages
- Change favicon
- Login Page: Press enter in password field to login

### 2.0
- Backend: Use fastAPI
- Websocket: when authentication fails, go to login page
- Login Page: add tab key navigation between username and password fields in login form
- VmPage: Add option to show VM logs
- Notifications: Implement notifications
- VmPage: Fix bug where only 5 VMs were shown
- Login: Add setting to control token expiration time
- Storage: manage storage devices
- Storage: create partition on storage device
- RAID Management: manage RAID arrays
- Shared Folders: manage shared folders
- Shared Folders: SMB share
- Users: Manage system users & smb users
- General: use a new "DirectoryList" component to select directories or files
- VM Manager: Replace libvirt pools with "Shared Folders"
- Docker: Manage docker containers, images, volumes, networks and templates
