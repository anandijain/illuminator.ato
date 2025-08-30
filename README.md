# illuminator

TODO before order:
* fix mounting holes position
* cad enclosure and box 
* order the diffuser and lens

petri dish illuminator for timelapses 

the functionality basically has an 
* mcu turn on a bunch of lights
* light goes thru a diffuser
* hit the petri (excite the fluorescent protein)
* into a filter 
* imaged via timelapse on a DSLR 

there are two modes to use the device
Common to both modes is using a GPIO pin to turn on a mosfet that turns on an LED grid. 

## Raspberry Pi Pico 
the first is using a raspberry pi pico, and the second is using a full fledged Pi. 
However, we still need to tell the camera to take a photo while the lights are on. 
The pico accomplishes this by using a GPIO pin to drive an optocoupler, which connects to the [MC-DC2](https://www.dslrbodies.com/cameras/general-nikon-camera-info/nikon-mc-dc2-connector-pin.html) port. 
Basically the opto provides a short between the Tip and the Sleeve, triggering a photo to be taken.

## Raspberry Pi 
Unfortunately, this method requires providing power for the board and the Pi separately (two power cables). 
Basically, a USB cable is connects the Pi to Nikon's semi-proprietary UC-E6 "USB" port. 
Then we use `gphoto2` to trigger the camera and download it to the Pi.


the design is as follows, a 5V 5A (5A is excessive, you probably dont need more than 2-3A) wall wart plugs to a barrel jack

the barrel jack tip will go to VBus of the USB port and the 36 resistor-led pairs (all parallel)

the ground of the barrel goes to the gnd of the USB. 

The usb is an TYPE-A connector that is used solely for powering the Pico (DO NOT USE FOR A FULL PI, the USB 2.0 spec is limited at 1.5A but a Pi can draw 5A.)

There is a TRS (i dont like JST) port used for connecting GPIO from Pi/Pico to the board.
The Tip of `trs_sig` is only used by the pico, and is for turning on the optocoupler
The Ring is used by both for turning on the FET (the LEDs)
The Sleeve is GND. 

A second TRS connector is used to connect the MC-DC2 connector from camera to the optocoupler. Unfortunately, it seems common that MC-DC2 uses a 2.5mm TRS, but I am just going to use an adapter so that I don't need to buy 2.5mm jacks that I'll never use. 

The path is 5v -> (R -> LED)* -> FET_DRAIN -> FET_SOURCE -> GND.


### 8/28/25 

the general design will be relatively agnostic to the excitation wavelength, 
allowing multiple different proteins to be timelapsed 

TODO:
- resistor sizing for each string of LEDs
- can i PWM my N-mosfet that controls the leds? 

https://chatgpt.com/share/68b0b650-5c54-8009-a0fc-7b128db387fa


even though the excitation peak of [A. Victoria's GFP gene](https://www.fpbase.org/protein/avgfp/) is at 395 nm (UVA range), 
there is evidence that photobleaching occurs and can inhibit cell growth.

that, in addition to the eyes/skin risk of penetrating UV, we will use the weaker excitation peak of 
475 nm 


there are two primary routes to acheiving timelapses, 

the first is using a Pico and a port on the D7100 called MC-DC2 

the second is using a full RPi with gphoto2, this allows the collection of the photos onto the Pi


after extensive reading: the grid of LEDs will be 12 strings of 3 LEDs, powered by a 12V rail

maybe instead of a buck since it seems sparse to find preset 5V bucks at 3A (enought to power Pi)
and the ones that are adjustable seem annoying to implement

if we are going with the Pico, then its a bit easier since it's not going to need 5V 3A.


math

datasheet of led -> radiative flux (mW) -> photons/sec

concentration of GFP + QY + photons/sec -> number of emitted photons/sec 

