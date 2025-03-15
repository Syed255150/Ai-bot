import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import subprocess
import logging
import datetime
import time
import sys,os
from fb_ads_automate import main
# Configure logging
# logging.basicConfig(filename='scheduler.log', level=logging.INFO, format='%(asctime)s %(message)s')
# logger = logging.getLogger(__name__)


def get_scheduled_tasks():
    """Retrieve all pending scheduled tasks from the database."""
    with sqlite3.connect('fb_ads_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts, schedule_datetime FROM schedule WHERE status = 'Pending'")
        tasks = cursor.fetchall()
    return tasks

def update_task_status(task_id, status):
    """Update the status of a task in the database."""
    with sqlite3.connect('fb_ads_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Schedule SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

def run_facebook_automation(task_id, group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts):
    """Run the fb_ads_automate.py script with the given parameters."""
    # try:
    #     cmd = [
    #         'python', 'fb_ads_automate.py',
    #         str(group_id), str(additional_number), str(random_renew_number),
    #         str(random_price), str(delete_relist), str(posting_speed)
    #     ]
    #     subprocess.run(cmd, check=True)
    #     # logger.info(f"Executed fb_ads_automate.py with params: {cmd}")
    #     update_task_status(task_id, 'Completed')
    # except subprocess.CalledProcessError as e:
    #     # logger.error(f"Error executing fb_ads_automate.py: {e}")
    #     update_task_status(task_id, 'Failed')
    try:
        # cmd = [
            # 'python', os.path.join(get_base_path(), 'fb_ads_automate.py'),
            # os.path.join(get_base_path(), 'fb_ads_automate.exe'),
            # str(group_id), str(additional_number), str(random_price), 
            # str(posting_speed), str(post_action), str(shuffle_accounts)]
        
        # subprocess.run(cmd, check=True)

        main(group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts)

        update_task_status(task_id, 'Completed')
    except subprocess.CalledProcessError as e:
        update_task_status(task_id, 'Failed')

def schedule_tasks(scheduler):
    """Schedule tasks based on the database entries."""
    tasks = get_scheduled_tasks()

    for task in tasks:
        task_id, group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts, schedule_datetime = task
        schedule_time = datetime.datetime.strptime(schedule_datetime, '%Y-%m-%d %H:%M:%S')

        if not scheduler.get_job(str(task_id)):
            trigger = DateTrigger(run_date=schedule_time)
            scheduler.add_job(
                run_facebook_automation,
                trigger,
                args=[task_id, group_id, additional_number, random_price, posting_speed, post_action, shuffle_accounts],
                id=str(task_id),
                name=f"Task {task_id}",
                replace_existing=True
            )
            # logger.info(f"Scheduled task {task_id} at {schedule_time}")

def periodic_schedule_check(scheduler):
    """Periodically check for new tasks and schedule them."""
    while True:
        schedule_tasks(scheduler)
        time.sleep(60)  # Sleep for 60 seconds

if __name__ == '__main__':
    print("start scheduler in the background")
    scheduler = BackgroundScheduler()
    scheduler.start()
    # logger.info("Scheduler started.")
    
    try:
        periodic_schedule_check(scheduler)
    except (KeyboardInterrupt, SystemExit):
        # Handle script interruption
        # logger.info("Scheduler stopped.")
        scheduler.shutdown()
