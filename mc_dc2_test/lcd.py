from machine import Pin, SPI, PWM
import time
import st7789py as st7789
import vga1_8x8 as font

params = {"interval [s]": 30, "duration [hr]": 36}
param_keys = list(params)
N_PARAMS = len(params)
TEXT_H = TEXT_W = 8

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
for i, key in enumerate(param_keys):
    prefix = "> " if i == cursor_idx else "  "
    tft.text(font, "{}{}: {}".format(prefix, key, params[key]), 0, i*TEXT_H)

def incr_cb(p):
    global params, param_keys, cursor_idx
    params[param_keys[cursor_idx]] += 1
    

def decr_cb(p):
    global params, param_keys, cursor_idx
    params[param_keys[cursor_idx]] -= 1

    
def next_cb(p):
    global cursor_idx
    cursor_idx = (cursor_idx + 1) % N_PARAMS
    print("new cursor index: ", cursor_idx)

decr = Pin(20, Pin.IN, Pin.PULL_UP)
incr = Pin(19, Pin.IN, Pin.PULL_UP)
next = Pin(18, Pin.IN, Pin.PULL_UP)

decr.irq(trigger=Pin.IRQ_RISING, handler=decr_cb)
incr.irq(trigger=Pin.IRQ_RISING, handler=incr_cb)
next.irq(trigger=Pin.IRQ_RISING, handler=next_cb)

i = 0
while True:
    print(i, ": decr: ", decr.value(), " incr: ", incr.value(), " next: ", next.value())
    time.sleep(.1)
    i += 1