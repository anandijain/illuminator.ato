using DynamicQuantities
const C = Constants
power_per_cm2 = .5u"mW/(cm^2)"
plate_diam = 10u"mm" # roughly, we can look up true value later
plate_area = π * (plate_diam/2)^2

power_for_plate = power_per_cm2 * plate_area
uconvert(us"mW", power_for_plate) 
# need to account for losses in the diffuser, etc
λ = 475u"nm"
E_ph = (C.h * C.c)/λ


# the candela is actually weighted by the eye sensitivity, who knew?! 
# https://en.wikipedia.org/wiki/Luminous_efficiency_function
# in a way, for this application candela is kinda a bad unit since it is weighted by eye sensitivity
# but we care about actual photons at specific frequencies. 

# there is a difference between radiometric and photometric units and conversion is tricky
# the general strat is candela (cd) -> lumens (lm) -> watts (W)

lum_intens_led = 50u"mcd"

# apparently an "emission model" is needed to convert to lm 
# https://en.wikipedia.org/wiki/Lambert%27s_cosine_law#/media/File:Lambert_Cosine_Law_1.svg

# chat gives that 
# phi_v = .191u"cd*sr"# lumen (apparently not in DQ package)
phi_v = .191

#lumens -> watts
V_475  = .118

phi_e = (phi_v/(683 * V_475))u"W"
uconvert(us"mW", phi_e)

# we now have the number of 475nm photons per second emitted by one led
n_photons_per_led_per_second = .00237 / ustrip(E_ph)

Td = .6 # diffuser transmission

phot_per_s_after_diffuser = n_photons_per_led_per_second* Td


cell_conc = 1e9 # stationary 
gfp_copy_num_per_cell = 1e5 

gfp_uM = .166 