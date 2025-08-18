import time
import logging
import schedule
from daily_scheduler import DailyScheduler

logger = logging.getLogger("autobus_tracker")
logger.info("Bus delay monitor starting")


scheduler_pezinok = DailyScheduler("bus_527_Pezinok.json")
scheduler_bratislava = DailyScheduler("bus_527_Bratislava.json")
screen_content = scheduler_pezinok.get_screen_content()
screen_content.update(scheduler_bratislava.get_screen_content())

# sort screen_content by selectedDeparture
screen_content = dict(sorted(screen_content.items(), key=lambda item: item[1]['selectedDeparture']))

# Keep the script running
while True:
    schedule.run_pending()

    time.sleep(1)