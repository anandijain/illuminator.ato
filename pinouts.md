## buttons
from the left buttons numbered b1-b5 
all buttons use PULL UP
from right takes up GP0-4
the button gnd is on 


button board gnd <-> RPI8
b1 <-> GP4 RPI6
b2 <-> GP3 RPI5
b3 <-> GP2 RPI4
b4 <-> GP1 RPI2
b5 <-> GP0 RPI1

## LCD

bl <-> GP6 
rst <-> GP7
dc <-> GP8
cs <-> GP9
clk <-> GP10
din <-> GP11
gnd <-> RPI18
vcc <-> RPI 36

## pico <-> pcb
### trs
tip <-> GP26
ring <-> GP27
sleeve <-> GND (RPI 33)

### power (from the usb cable)
gnd <-> GND (RPI 38)
5v <-> VSYS (Rpi 39)
