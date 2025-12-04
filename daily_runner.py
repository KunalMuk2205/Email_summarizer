import schedule
import time
from summarize import run_daily_summary

def run_scheduler():
    schedule.every().day.at("14:00").do(run_daily_summary)
    print("Scheduler started...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()