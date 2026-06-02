from app.core.scheduler import scheduler
import time

scheduler.start()

print("Scheduler started...")

try:
    while True:
        time.sleep(60)

except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()