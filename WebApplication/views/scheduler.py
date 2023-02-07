import datetime

from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler


def set_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    return scheduler
