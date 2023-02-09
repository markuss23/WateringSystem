import datetime

from apscheduler.schedulers.background import BackgroundScheduler


def set_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    return scheduler


def job_function():
    print("text", str(datetime.datetime.now()))


def run_cron():
    scheduler = set_scheduler()
    scheduler.add_job(job_function, 'cron', day_of_week='mon-fri', hour=17, minute='53-54')
    scheduler.start()
