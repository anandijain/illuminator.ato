from machine import Pin
import time
import math

OPTO_PIN = Pin(16, Pin.OUT)
FET_PIN  = Pin(17, Pin.OUT)
LED      = Pin("LED", Pin.OUT)

def on_off(p, delay=0.1):
    p.value(1)
    time.sleep(delay)
    p.value(0)
    time.sleep(delay)

def snap():
    # Example: gate power on, pulse opto, gate off
    FET_PIN.value(1)
    on_off(OPTO_PIN, delay=0.3)
    FET_PIN.value(0)
    LED.toggle()  # visual heartbeat

def timelapse(interval, duration):
    """
    interval: seconds between snaps (float ok)
    duration: total run time in HOURS, or the string "forever"
    """
    if duration == "forever":
        next_t = time.ticks_ms()
        while True:
            snap()
            next_t = time.ticks_add(next_t, int(interval * 1000))
            time.sleep_ms(max(0, time.ticks_diff(next_t, time.ticks_ms())))
        # never returns

    dur_sec = duration * 3600  # duration is in HOURS per docstring
    num_snaps = math.ceil(dur_sec / interval)

    next_t = time.ticks_ms()
    for i in range(num_snaps):
        snap()
        if i == num_snaps - 1:
            break  # don't sleep after last snap
        next_t = time.ticks_add(next_t, int(interval * 1000))
        time.sleep_ms(max(0, time.ticks_diff(next_t, time.ticks_ms())))
