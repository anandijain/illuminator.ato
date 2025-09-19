from machine import Pin, SPI, PWM
import time
import st7789py as st7789
# import vga1_8x8 as font
# import vga1_16x16 as font
import vga2_16x32 as font
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

params = {"interval [s]": 30, "duration [hr]": 36}
param_keys = list(params)
N_PARAMS = len(params)

spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))

dc  = Pin(8,  Pin.OUT)
cs  = Pin(9,  Pin.OUT)
rst = Pin(12, Pin.OUT)

bl = PWM(Pin(13)); bl.freq(1000); bl.duty_u16(65535)

tft = st7789.ST7789(spi, 240, 320, reset=rst, dc=dc, cs=cs, rotation=1)
tft.fill(st7789.RED)

interval = 30
dur_hr = 36

cursor_idx = 0
def draw():
    for i, key in enumerate(param_keys):
        prefix = "> " if i == cursor_idx else "  "
        tft.text(font, "{}{}: {}".format(prefix, key, params[key]), 0, i*font.HEIGHT)
draw()

change_delta = 0   # -1, 0, +1 pending changes for current field
next_pending = False
start_pending = False

def incr_cb(p):
    global change_delta
    change_delta += 1     # simple integer change is safe

def decr_cb(p):
    global change_delta
    change_delta -= 1

def next_cb(p):
    global next_pending
    next_pending = True

def start_cb(p):
    global start_pending
    start_pending = True
    # print("starting timelapse")


decr = Pin(21, Pin.IN, Pin.PULL_UP)
incr = Pin(20, Pin.IN, Pin.PULL_UP)
next = Pin(19, Pin.IN, Pin.PULL_UP)
start = Pin(18, Pin.IN, Pin.PULL_UP)

decr.irq(trigger=Pin.IRQ_RISING, handler=decr_cb)
incr.irq(trigger=Pin.IRQ_RISING, handler=incr_cb)
next.irq(trigger=Pin.IRQ_RISING, handler=next_cb)
start.irq(trigger=Pin.IRQ_RISING, handler=start_cb)

last_apply = time.ticks_ms()
APPLY_EVERY_MS = 30   # small debounce / coalesce window

while True:
    try: 
        now = time.ticks_ms()

        # handle "next" (change selected field)
        if next_pending:
            next_pending = False
            cursor_idx = (cursor_idx + 1) % N_PARAMS
            draw()
        if start_pending: 
            next_pending = False
            tft.text(font, "starting timelapse...", 0, (N_PARAMS+1)*font.HEIGHT)
            timelapse(params["interval [s]"], params["duration [hr]"])
        # coalesce +/- presses and apply periodically (debounce-ish)
        if change_delta != 0 and time.ticks_diff(now, last_apply) >= APPLY_EVERY_MS:
            key = param_keys[cursor_idx]
            params[key] += change_delta
            change_delta = 0
            last_apply = now
            draw()

        time.sleep_ms(5)
    except KeyboardInterrupt:
        break
