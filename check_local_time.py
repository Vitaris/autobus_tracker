import datetime
import socket
import time

import ntplib

DRIFT_WARNING_SECONDS = 2  # threshold to warn about clock drift

def get_time_via_ntp(server: str = "pool.ntp.org", timeout: float = 3.0):
    client = ntplib.NTPClient()
    try:
        response = client.request(server, version=3, timeout=timeout)
        return datetime.datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)
    except (ntplib.NTPException, OSError, socket.timeout) as e:
        print(f"NTP failed ({server}): {e}")
        return None

def get_network_time():
    ntp_servers = ["pool.ntp.org", "time.google.com", "time.windows.com"]
    for srv in ntp_servers:
        dt = get_time_via_ntp(srv)
        if dt:
            return dt
    return None

def get_local_utc_time() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def compare_local_and_network_time():
    net = get_network_time()
    local = get_local_utc_time()
    if net is None:
        return False
    drift = (local - net).total_seconds()
    abs_drift = abs(drift)
    return abs_drift <= DRIFT_WARNING_SECONDS

def check_local_time():
    for _ in range(5):
        if compare_local_and_network_time():
            return True
        print("Clock drift detected. Retrying...")
        time.sleep(60)
    print("Clock drift too large after retries.")
    return False
