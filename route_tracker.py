from enum import Enum, auto
import requests
import schedule


class STATUS(Enum):
    UNINITIALIZED = auto()
    DEPARTING = auto()
    IN_TRANSIT = auto()
    APPROACHING = auto()
    ARRIVED = auto()
    DELAYED = auto()
    CANCELLED = auto()

class BusTracker:
    def __init__(self, coordinates, line):
        self.status = STATUS.UNINITIALIZED
        self.coordinates = coordinates
        self.line = line
        self.trip_id = None
        self.trip_nr = None
        self.get_trip_id()
        self.current_delay = None

        if self.trip_id:
            self.get_delay()
            schedule.every(10).seconds.do(self.get_delay)
        else:
            print('No line found')

    def get_trip_id(self):
        # The API endpoint (you'll need to provide the actual URL)
        url = f"https://mapa.idsbk.sk/navigation/vehicles/nearby?{self.coordinates}&cityID=-1"  # Replace with your actual API URL

        try:
            # Make the GET request
            response = requests.get(url)

            # Check if request was successful
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                for vehicle in data['vehicles']:
                    print(f"debug {vehicle['timeTableTrip']['timeTableLine']['line']}")
                    if vehicle['timeTableTrip']['timeTableLine']['line'] != str(self.line):
                        break
                    self.trip_id = vehicle['timeTableTrip']['tripID']
                    self.trip_nr = vehicle['timeTableTrip']['trip']
            else:
                print(f"Error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def get_delay(self):
        # The API endpoint (you'll need to provide the actual URL)
        url = f"https://mapa.idsbk.sk/navigation/vehicles/get_real?tripID={str(self.trip_id)}&firmaID=806&line={str(self.line)}&tripNumber={str(self.trip_nr)}"  # Replace with your actual API URL

        try:
            # Make the GET request
            response = requests.get(url)

            # Check if request was successful
            if response.status_code == 200:
                # Parse JSON response
                data = response.json()
                self.current_delay = data['vehicle'].get('delayMinutes')
                print(self.current_delay)

            else:
                print(f"Error: {response.status_code}")
                self.current_delay = -1

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            self.current_delay = -1

