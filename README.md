# illuminator

petri dish illuminator for timelapses 

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

