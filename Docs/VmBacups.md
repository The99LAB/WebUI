# Backup Job
- Stored in database
- Create a backup Job
  - Enabled
  - Name
  - Schedule (optional)
  - storage 
  - virtual machines
    - disks not to backup
  - retention policy
    - keep all backups
    - keep last x backups

When a backup job is created or changed, the configuration should be written to the directory where the backup job data is stored.
This file will be named 'backup-job.json'

When a backup job is started:
    - Send a notification that the job has started
    - Run the backup job
    - Send a notification that the job has finished (success or failure)


# Execute Job
- Get the directory where the backup will be stored
- Make a new directory with the current date and time
    - Create the backup-job.json file to the new directory
    - Create a new log file called 'backup-job.log'
    - Write the status of the backup job to the 'backup-job.json' file
    - For each virtual machine in the backup job:
        - Create a folder for the virtual machine in the backup directory
        - If the virtual machine is running, stop it
        - Copy the virtual machine xml file to the folder
        - Copy the virtual machine disk files to the folder
        - If the virtual machine was running, start it



# Restore Job



# Restore Job external
- Let the user select the backup-job.json file
- Restore it