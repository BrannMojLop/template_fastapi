import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logging.basicConfig(
    filename="job_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize the background scheduler
scheduler = BackgroundScheduler()

functions_to_run = []

def start_jobs():
    for func in functions_to_run:
        try:
            func()
        except Exception as e:
            logging.error(f"Error executing {func.__name__}: {str(e)}")


# scheduler.add_job(start_jobs, trigger=IntervalTrigger(hours=1))

