# -*- coding: utf-8 -*-
"""
AD5791 Voltage Source
=====================================
:Author: Larry Chen and Chunyang Ding
"""

from slab.instruments import SerialInstrument, Instrument
import time


class AD5791(SerialInstrument):
    default_port = 23

    def __init__(self, name='AD5791', address='', enabled=True, timeout=1, recv_length=1024):
        SerialInstrument.__init__(self, name, address, enabled=enabled, timeout=timeout, recv_length=recv_length)
        self.query_sleep=0.01

    def initialize(self, channel=None):
        if channel is None:
            return self.query('INIT')
        else:
            return self.query('INIT %d' %(int(channel)))

    def set_voltage(self, channel, voltage):
        bitcode = int((voltage/20.)*1048576 + 524288)
        print('set target', bitcode)
        if bitcode < 0 or bitcode > 1048576:
            print('ERROR: voltage out of range')
            return bitcode
        self.query('SET %d %d' % (channel, bitcode))

    def get_voltage(self, channel):
        return self.query('READ %d' % (channel))

    #Remove checks, feedback from DAC on ramp due to readout not working
    # def ramp(self, channel, voltage, speed):
    #     """Ramp to voltage with speed in (V/S)"""
    #     bitcode = int((voltage + 10.0)*13107.2)
    #     print('target', bitcode)
    #     time.sleep(self.query_sleep)
    #     if bitcode < 0 or bitcode > 1048576:
    #         print('ERROR: voltage out of range')
    #         return str(bitcode)
    #     step_size = 10 # in bits, about 0.7mV out of +-10V
    #     step_time = int(step_size * 0.0762939453 / speed)
    #     if step_time == 0:
    #         step_time = 1
    #     endbit = self.query('RAMP %d %d %d %d' % (channel, bitcode, step_size, step_time))
    #     print('end of ramp -', endbit)
    #     time.sleep(self.query_sleep)
    #     return endbit


    def get_id(self):
        """Get Instrument ID String"""
        return self.query('ID')

    def sweep(self, channel):
        time.sleep(self.query_sleep)
        self.query('SET %d 0' % channel)
        time.sleep(self.query_sleep)
        self.query('RAMP %d %d %d %d' % (channel, 262143, 100, 500))
        time.sleep(self.query_sleep)
        self.query('RAMP %d %d %d %d' % (channel, 0, 100, 500))
        return self.query('READ %d' % (channel))
    
    def hello(self):
        print("hello")
        return 0.0

if __name__ == "__main__":
    """Test script"""
    dac = AD5791(address='COM13')
    #dac = AD5780(address='192.168.14.253')
    print((dac.get_id()))

    dac.initialize()
    dac.set_voltage(2, 1)
#     time.sleep(1)
#     i = 1
#     print("Channel = %s"%i)
#     dac.set_voltage(1, 1.2)
    #dac.ramp(i,0.1,0.1)

