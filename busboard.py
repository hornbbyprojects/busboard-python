import tfl
import screen
import time
import math
import urequests
import machine
import socket
import gc

button = machine.Pin(26, machine.Pin.PULL_DOWN)

TIME_URL = "https://www.timeapi.io/api/TimeZone/zone?timeZone=UTC"

TICK_TIME_MILLISECONDS = 5
TICKS_PER_SECOND = 1000 / TICK_TIME_MILLISECONDS
TICKS_UPDATE_TIME = TICKS_PER_SECOND * 10
TICKS_UPDATE_CACHE = TICKS_PER_SECOND * 30

def convert_time_to_rtc_format(t):
    lf = time.localtime(t) # localtime format
    return (lf[0], lf[1], lf[2], lf[6], lf[3], lf[4], lf[5], 0)
    
def set_time():
    # Ignore network latency, we just want a rough estimate
    print(f"Getting time...")
    gc.collect()
    try:
        response = urequests.get(TIME_URL).json()
    except OSError as e:
        print(f"Error OS {e.errno}")
    print("Got time...")
    time_str = response["currentLocalTime"] + "Z"
    print(time_str)
    t = convert_time_to_rtc_format(tfl.parse_time(time_str)) # forgive me
    machine.RTC().datetime(t)
        

if __name__ == "__main__":
    screen.init()
    screen.write_string("Connecting...")
    tfl.connect()
    screen.clear()
    screen.write_string("Getting time...")
    try:
        set_time()
        screen.clear()
        screen.write_string("Getting buses...")
        def delta_string(bus):
            return f"{bus.line_id}~{bus.destination[:4]} in " + str(int(math.ceil((bus.time - time.time())/60)))

        update_cache_counter = 0
        update_time_counter = 0
        tfl.update_cache()
        while True:
            if(button.value() == 1):
                print("switch")
                tfl.change_current_stop()
            update_time_counter = update_time_counter + 1
            if button.value() == 1 or update_time_counter == TICKS_UPDATE_TIME:
                print("redraw")
                update_time_counter = 0
                buses = tfl.get_buses()
                screen.clear()
                if len(buses) > 0:
                    screen.write_string(delta_string(buses[0]))
                    if len(buses) > 1:
                        screen.newline()
                        screen.write_string(delta_string(buses[1]))
                else:
                    screen.write_string("No buses")
            update_cache_counter = update_cache_counter + 1
            if update_cache_counter == TICKS_UPDATE_CACHE:
                update_cache_counter = 0
                print("updating cache...")
                gc.collect()                
                tfl.update_cache_async()
            time.sleep_ms(TICK_TIME_MILLISECONDS)
    except Exception as e:
        raise e
    except Exception as e:
        screen.clear()
        screen.write_string("ERROR"+str(e))
