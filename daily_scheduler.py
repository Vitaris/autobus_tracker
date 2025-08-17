from check_local_time import check_local_time
import datetime
import holidays 
import os

_sk_holidays = holidays.country_holidays("SK")

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
        pass
        

    def is_workday(self):
        # Check if the day is a weekend
        if self.today.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False

        # Check if the day is a public holiday
        if self.today in _sk_holidays:
            return False
        
        return True

    def is_summer_holiday(self):
        # Check if the day is within the summer or autumn holiday period
        summer_start = datetime.date(self.today.year, 6, 30)
        summer_end = datetime.date(self.today.year, 8, 29)
        autumn_start = datetime.date(self.today.year, 10, 30)
        autumn_end = datetime.date(self.today.year, 10, 31)

        return (summer_start <= self.today <= summer_end) or (autumn_start <= self.today <= autumn_end)

if __name__ == "__main__":
    try:
        scheduler = DailyScheduler("bus_527_Bratislava.json")
    except InvalidLocalTimeError as e:
        print(f"Scheduler not started: {e}")
    else:
        print(f'workday: {scheduler.workday}, summer_holiday: {scheduler.summer_holiday}')
