from machine import Pin
import time

OPTO_PIN = Pin(16, Pin.OUT)
FET_PIN = Pin(17, Pin.OUT)
LED = Pin("LED", Pin.OUT)

def on_off(p, delay=0.1):
    p.value(1)
    time.sleep(delay)
    p.value(0)
    time.sleep(delay)

def snap():
    FET_PIN.value(1)
    on_off(OPTO_PIN, delay=.3)
    FET_PIN.value(0)

snap()