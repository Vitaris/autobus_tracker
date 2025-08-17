import datetime
import holidays 
import os
from check_local_time import check_local_time
import json
from pathlib import Path
from typing import Optional, Tuple

_sk_holidays = holidays.country_holidays("SK")

def read_json(path):
    p = Path(path)
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)  # dict or list, depending on the file
    except FileNotFoundError:
        print(f'File not found: {p}')
    except json.JSONDecodeError as e:
        print(f'Invalid JSON in {p}: {e}')
    except PermissionError:
        print(f'No permission to read: {p}')
    return None

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
        self.schedule_daily_tasks()

    def schedule_daily_tasks(self):
        data = read_json(self.travel_schedule)
        if not data or 'Trips' not in data:
            print("No trips to schedule.")
            return
        now = datetime.datetime.now() - datetime.timedelta(hours=8)
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

            # Here you would schedule the job; for now just print
            minutes = delta.total_seconds() / 60.0
            print(f"Scheduling trip id={trip.get('id')} at {dep} in {minutes:.1f} minutes (service={service})")

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

if __name__ == "__main__":
    try:
        scheduler = DailyScheduler("bus_527_Pezinok.json")
        scheduler = DailyScheduler("bus_527_Bratislava.json")
    except InvalidLocalTimeError as e:
        print(f"Scheduler not started: {e}")
    else:
        print(f'workday: {scheduler.workday}, summer_holiday: {scheduler.summer_holiday}')
        # Simple direct check example:
        is_future, delta = compare_departure_today("07:15")
        print(f"07:15 future_or_now={is_future} delta_seconds={delta.total_seconds():.0f}")
