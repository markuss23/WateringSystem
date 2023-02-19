from apscheduler.schedulers.background import BackgroundScheduler


def get_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    return scheduler









