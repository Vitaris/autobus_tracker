import os
import datetime
import holidays 
import json
import schedule
import time
import logging
from route_tracker import BusTracker
from pathlib import Path
from typing import Optional, Tuple
from check_local_time import check_local_time

_sk_holidays = holidays.country_holidays("SK")
logger = logging.getLogger("autobus_tracker")

shopping_palace_coordinates = 'lat=48.18775935062897&lng=17.182493638092055&radius=3.1674463090485787'
pezinok_coordinates = 'lat=48.28763726983306&lng=17.274096270366496&radius=3.1672252273331774'

def read_json(path):
    p = Path(path)
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)  # dict or list, depending on the file
    except FileNotFoundError:
        logger.error(f'File not found: {p}')
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in {p}: {e}')
    except PermissionError:
        logger.error(f'No permission to read: {p}')
    return None

def bus_to_PK_task():
    logger.info(f"Bus is departing at {datetime.datetime.now().strftime('%H:%M:%S')} - to PK")
    bus_tracker_pk = BusTracker(shopping_palace_coordinates, 527)
    # Add your monitoring logic here

def bus_to_SP_task():
    logger.info(f"Bus is departing at {datetime.datetime.now().strftime('%H:%M:%S')} - to SP")
    bus_tracker_sp = BusTracker(pezinok_coordinates, 527)
    # Add your monitoring logic here

def compare_departure_today(departure_str: str, now: Optional[datetime.datetime] = None) -> Tuple[bool, datetime.timedelta]:
    """
    Compare HH:MM departure (today) with current time.
    Returns (is_future_or_now, delta) where:
      is_future_or_now == True means departure is now or later today
      delta = departure_dt - now (positive or negative)
    """
    if now is None:
        now = datetime.datetime.now()  # local time
    try:
        hh, mm = map(int, departure_str.split(":"))
    except ValueError:
        raise ValueError(f"Invalid time format '{departure_str}', expected HH:MM")
    dep_dt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    delta = dep_dt - now
    return (delta.total_seconds() >= 0, delta)

class InvalidLocalTimeError(RuntimeError):
    pass

class DailyScheduler:
    def __init__(self, travel_schedule):
        if not os.path.exists(travel_schedule):
            raise FileNotFoundError(f"Travel schedule file '{travel_schedule}' not found.")
        self.travel_schedule = travel_schedule
        if not check_local_time():
            raise InvalidLocalTimeError("Local time check failed; refusing to schedule.")
        self.today = datetime.date.today()
        self.workday = self.is_workday()
        self.summer_holiday = self.is_summer_holiday()
        self.screen_content = {}
        self.schedule_daily_tasks()

    def schedule_daily_tasks(self):
        data = read_json(self.travel_schedule)
        if not data or 'Trips' not in data:
            logger.info("No trips to schedule.")
            return
        now = datetime.datetime.now()
        for trip in data['Trips']:
            dep = trip.get("initDeparture")
            is_future, delta = compare_departure_today(dep, now)
            if not is_future:
                continue
            service = trip.get("service")
            if self.workday:
                if service == "Weekends-Holidays":
                    continue
            else:
                if service == "Workdays":
                    continue

            if self.summer_holiday:
                if service == "Workdays-No-Summertime":
                    continue
            else:
                if service == "Workdays-Summertime":
                    continue

            logger.info(f"Scheduling trip id={trip.get('id')} at {dep}, (service={service})")
            schedule.every().day.at(dep).do(bus_to_SP_task)

            # Append to screen content
            self.screen_content[trip.get('id')] = {'selectedDeparture': trip.get('selectedDeparture'), 'finalStop': trip.get('finalStop')}

    def is_workday(self):
        if self.today.weekday() >= 5:  # 5=Sat, 6=Sun
            return False
        if self.today in _sk_holidays:
            return False
        return True

    def is_summer_holiday(self):
        summer_start = datetime.date(self.today.year, 6, 30)
        summer_end = datetime.date(self.today.year, 8, 29)
        autumn_start = datetime.date(self.today.year, 10, 30)
        autumn_end = datetime.date(self.today.year, 10, 31)
        return (summer_start <= self.today <= summer_end) or (autumn_start <= self.today <= autumn_end)

    def get_screen_content(self):
        return self.screen_content
