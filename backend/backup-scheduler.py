import vm_backups
from apscheduler.schedulers.background import BlockingScheduler
import apscheduler.jobstores.base
from datetime import datetime

def parse_cron_expression(cron_expression):
    minute, hour, day_of_month, month, day_of_week = cron_expression.split()
    cron_args = {
        'minute': minute,
        'hour': hour,
        'day': day_of_month,
        'month': month,
        'day_of_week': day_of_week,
    }
    return cron_args

def refresh_and_schedule_jobs():
    print("Refreshing and scheduling jobs")
    backup_jobs = backup_job_manager.get_all_backup_jobs()

    for backup_job in backup_jobs:
        if not backup_job.enabled or backup_job.schedule.cron_expression is None:
            print(f"Skipping job {backup_job.name}")
        else:
            try:
                scheduler.add_job(
                    run_backup_job, 
                    trigger='cron', 
                    id=str(backup_job.id), 
                    args=[backup_job.name],
                    **parse_cron_expression(backup_job.schedule.cron_expression)
                )
                print(f'Scheduled job {backup_job.name} with cron expression {backup_job.schedule.cron_expression}')
            except apscheduler.jobstores.base.ConflictingIdError:
                print(f'Job already scheduled {backup_job.name}')

def run_backup_job(name):
    print(f"Running backup job {name}: {datetime.now()}")
    try:
        backup_job_manager.start_backup_job(name)
        print(f"Finished backup job {name}")
    except vm_backups.jobManagerException:
        print(f"Failed to run backup job {name}")
    
if __name__ == '__main__':
    print("Starting scheduler")
    scheduler = BlockingScheduler()
    backup_job_manager = vm_backups.BackupJobManager()
    refresh_and_schedule_jobs()
    scheduler.add_job(refresh_and_schedule_jobs, 'interval', minutes=5)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
