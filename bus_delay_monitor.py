import schedule
import datetime
import time
from route_tracker import BusTracker

shopping_palace_coordinates = 'lat=48.18775935062897&lng=17.182493638092055&radius=5.0'
pezinok_coordinates = 'lat=48.28605918695282&lng=17.274160813385024&radius=5.0'

departure_527_SP_to_Pezinok = [
    datetime.time(5, 45),
    datetime.time(6, 15),
    datetime.time(6, 45),
    datetime.time(7, 15),
    datetime.time(8, 15),
    datetime.time(9, 15),
    datetime.time(10, 15),
    datetime.time(11, 15),
    datetime.time(12, 15),
    datetime.time(13, 15),
    datetime.time(13, 45),
    datetime.time(14, 15),
    datetime.time(14, 45),
    datetime.time(15, 15),
    datetime.time(15, 45),
    datetime.time(16, 15),
    datetime.time(16, 45),
    datetime.time(17, 15),
    datetime.time(18, 15),
    datetime.time(19, 15),
    datetime.time(20, 15),
    datetime.time(21, 15)
]
departure_527_Pezinok_to_SP = [
    datetime.time(4, 34),
    datetime.time(5, 24),
    datetime.time(6, 24),
    datetime.time(6, 54),
    datetime.time(7, 24),
    datetime.time(7, 54),
    datetime.time(8, 54),
    datetime.time(10, 54),
    datetime.time(12, 54),
    datetime.time(12, 59), # debug
    datetime.time(13, 24),
    datetime.time(13, 54),
    datetime.time(14, 54),
    datetime.time(15, 54),
    datetime.time(16, 54),
    datetime.time(17, 54),
    datetime.time(18, 54),
    datetime.time(20, 54)
]

def bus_to_PK_task():
    print(f"Bus is departing at {datetime.datetime.now().strftime('%H:%M:%S')} - to PK")
    bus_tracker_pk = BusTracker(shopping_palace_coordinates, 527)
    # Add your monitoring logic here

def bus_to_SP_task():
    print(f"Bus is departing at {datetime.datetime.now().strftime('%H:%M:%S')} - to SP")
    # bus_tracker_sp = BusTracker(pezinok_coordinates, 527)
    bus_tracker_sp = BusTracker(pezinok_coordinates, 610)
    # Add your monitoring logic here

# Schedule the task for each departure time
for departure in departure_527_SP_to_Pezinok:
    schedule.every().day.at(departure.strftime("%H:%M")).do(bus_to_PK_task)

# Schedule the task for each departure time
for departure in departure_527_Pezinok_to_SP:
    schedule.every().day.at(departure.strftime("%H:%M")).do(bus_to_SP_task)

bus_tracker_sp = BusTracker(pezinok_coordinates, 506)
# Keep the script running
while True:
    schedule.run_pending()

    time.sleep(1)