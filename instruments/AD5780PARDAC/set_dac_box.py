
from slab.instruments import AD5780_serial
import time
dac = AD5780_serial()
flux_list = [0, 0, 0, 0, 0, 0, 0.0, 0]
zero_list = [0, 0, 0, 0, 0, 0, 0.0, 0]
#flux_list = [4, 0,  0,  0,  0, 0, 0,  0]
#flux_list = [0.0]*8

print("Setting DAC Box")
# dac.init()
# time.sleep(1)
dac.parallelramp(flux_list,stepsize = 8,steptime = 1)
dac.parallelramp(zero_list,stepsize = 8,steptime = 1)
# dac.init()
# time.sleep(1)
# dac.set(1, 1.0)