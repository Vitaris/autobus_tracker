import time
from enum import Enum, auto
import requests
import schedule
from datetime import datetime, timezone
import dateutil.parser
import logging
from logging.handlers import RotatingFileHandler

# Shared logger for all BusTracker instances
logger = logging.getLogger("autobus_tracker")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _fh = RotatingFileHandler(
        "bus_tracker.log",
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=5,
        encoding="utf-8"
    )
    _fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    _fh.setFormatter(_fmt)
    logger.addHandler(_fh)
    logger.propagate = False

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
        self.current_delay = None
        # attach shared logger
        self.logger = logger
        # keep reference to the scheduled job
        self._delay_job = None
        self._job_tag = None

        self.logger.info(f"Initializing BusTracker line={self.line}, coords='{self.coordinates}'")
        for i in range(10):
            self.get_trip_id()
            if self.trip_id:
                self.logger.info(f"Found trip ID for line={self.line}: {self.trip_id}, tripNr={self.trip_nr}")
                break
            else:
                self.logger.warning(f"Attempt {i+1}/10: No trip ID found for line={self.line}, retrying...")
                time.sleep(60)

        if self.trip_id:
            self._job_tag = f"delay:{self.line}:{self.trip_id}"
            self.logger.info(f"Starting delay polling for line={self.line}, tripID={self.trip_id}, tripNr={self.trip_nr}")
            self.get_delay()
            self._delay_job = schedule.every(1).minutes.do(self.get_delay).tag("get_delay", self._job_tag)
        else:
            self.logger.warning(f"No line found for line={self.line} with coords='{self.coordinates}'")

    def get_trip_id(self):
        # The API endpoint (you'll need to provide the actual URL)
        url = f"https://mapa.idsbk.sk/navigation/vehicles/nearby?{self.coordinates}&cityID=-1"  # Replace with your actual API URL

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for vehicle in data['vehicles']:
                    self.logger.debug(f"nearby line: {vehicle['timeTableTrip']['timeTableLine']['line']}")
                    if vehicle['timeTableTrip']['timeTableLine']['line'] != str(self.line):
                        # vehicle['timeTableTrip']['timeTableLine']['line'] != f'101{str(self.line)}':
                        continue
                    self.trip_id = vehicle['timeTableTrip']['tripID']
                    self.trip_nr = vehicle['timeTableTrip']['trip']
                    self.logger.info(f"Found trip for line={self.line}: tripID={self.trip_id}, tripNr={self.trip_nr}")
                    break
            else:
                self.logger.error(f"Nearby request failed with status {response.status_code} (url={url})")
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Nearby request error for line={self.line}: {e}")

    def get_delay(self):
        # The API endpoint (you'll need to provide the actual URL)
        url = f"https://mapa.idsbk.sk/navigation/vehicles/get_real?tripID={str(self.trip_id)}&firmaID=806&line={str(self.line)}&tripNumber={str(self.trip_nr)}"  # Replace with your actual API URL

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.current_delay = data['vehicle'].get('delayMinutes')
                last_comm = data['vehicle']['lastCommunication']
                last_stop = data['vehicle']['lastStopOrder']
                self.logger.info(f"Delay update line={self.line} tripID={self.trip_id} tripNr={self.trip_nr}: stop={last_stop} delay={self.current_delay} min, lastComm={last_comm}")

                latitude = int(data['vehicle']['latitude'])
                longitude = int(data['vehicle']['longitude'])

                if latitude == 0 or longitude == 0:
                    if self._delay_job:
                        try:
                            schedule.cancel_job(self._delay_job)
                        except Exception:
                            pass
                        self._delay_job = None
                    self.logger.warning(f"Trip for line {self.line} (ID: {self.trip_id}) has completed. Stopping delay monitoring.")
            else:
                self.logger.error(f"get_real failed with status {response.status_code} (url={url})")
                self.current_delay = -1
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"get_real request error for line={self.line}: {e}")
            self.current_delay = -1

