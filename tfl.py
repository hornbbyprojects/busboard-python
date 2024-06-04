import network
import urequests
import time
import _thread
import gc

def arrivals_url(stop_id):
    return "https://api.tfl.gov.uk/StopPoint/" + stop_id + "/Arrivals"

golfids = ["490011752S", "490011752N"]
wlan = network.WLAN(network.STA_IF)
def connect():
    wlan.active(True)
    wlan.connect("Holophone-New", ";Fairy6342*")

class Bus:
    def __init__(self, line_id, destination, time):
        self.line_id = line_id
        self.destination = destination
        self.time = time

bus_cache = {}
bus_cache_lock = _thread.allocate_lock()
already_updating_lock = _thread.allocate_lock()
current_stop_index = 0
def update_cache():
    global bus_cache
    new_cache = {}
    current_time = time.time()
    for stop_id in golfids:
        print(f"Getting {stop_id}")
        try:
            r = urequests.get(arrivals_url(stop_id)).json()
        except OSError as e:
            print("Failed to get buses: " + str(e.errno))
            raise e
        except Exception as e:
            print("Failed to get buses: " + str(e))
            raise e
        print(r)
        for_stop = map(lambda x: Bus(x["lineId"], x["destinationName"], parse_time(x["expectedArrival"])), r)
        for_stop = list(filter(lambda x: x.time > current_time, for_stop))
        for_stop.sort(key=lambda x:x.time)
        new_cache[stop_id] = for_stop
    gc.collect()
    with bus_cache_lock:  
        bus_cache = new_cache
        
updating_cache = False
def update_cache_async():
    try:
        _thread.start_new_thread(update_cache, ())
    except OSError:
        return # If core in use, ignore

def get_buses():
    with bus_cache_lock:
        return bus_cache.get(golfids[current_stop_index]) or []

def change_current_stop():
    global current_stop_index
    new_stop_index = current_stop_index + 1
    if new_stop_index >= len(golfids):
        current_stop_index = 0
    else:
        current_stop_index = new_stop_index

def parse_time(str):
    assert str[-1] == "Z"
    str = str[:-1]
    [date, t] = str.split("T")
    [year, month, day] = date.split("-")
    [hour, minute, second] = t.split(":")
    return time.mktime((int(year), int(month), int(day), int(hour), int(minute), int(float(second)), None, None))
