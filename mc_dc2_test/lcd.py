from machine import Pin, SPI, PWM
import time
import st7789py as st7789

spi = SPI(1, baudrate=40_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))

dc  = Pin(8,  Pin.OUT)
cs  = Pin(9,  Pin.OUT)
rst = Pin(12, Pin.OUT)

bl = PWM(Pin(13)); bl.freq(1000); bl.duty_u16(65535)

# Constructor initializes the display (calls init internally) and clears it.
tft = st7789.ST7789(spi, 240, 320, reset=rst, dc=dc, cs=cs, rotation=1)

# Now you can draw
for _ in range(10):
    for color in (st7789.RED, st7789.GREEN, st7789.BLUE, st7789.WHITE, st7789.BLACK):
        tft.fill(color)
        time.sleep(0.5)
