import vm_backups


# LibvirtKVMBackup.BackupJobManager().start_backup_job('Ubuntu')

# print(LibvirtKVMBackup.BackupJobManager().list_job_timestamps('Ubuntu'))

# LibvirtKVMBackup.BackupJobManager().restore_backup_job('Ubuntu', '2023-08-19 16:08:35')

schedule = vm_backups.Schedule(
    cron_expression='0 22 * * *'
)

retention_policy = vm_backups.RetentionPolicy(
    vm_backups.RetentionPolicyType.KEEP_ALL
)

backup_job = vm_backups.BackupJob(
    name="Ubuntu",
    storage="/mnt/sharedfolders/vmbackups/UbuntuDesktop",
    retention_policy=retention_policy,
    schedule=schedule,
)

backup_job.add_vm(
    vm_backups.VirtualMachine(
        uuid='0c92cc15-2694-43a6-86fd-9e14bb23d9ea',
        disks=['sdb']
    )
)

backup_job_manager = vm_backups.BackupJobManager()

backup_job_manager.create_backup_job(backup_job)

print(backup_job_manager.get_all_backup_jobs())


