from slab.instruments.instrumenttypes import Instrument, VisaInstrument
#import os, time, sys
import numpy as np
#import Pyro4
import pyvisa as visa

class QDACII(VisaInstrument):
    def __init__(self, name, address='', enabled=True, timeout=1.0, **kwargs):
        Instrument.__init__(self, name, address, enabled, timeout, **kwargs)
        if self.enabled:
            self.protocol = 'VISA'
            self.timeout = timeout
            address = address.upper()
            self.instrument = visa.ResourceManager('@py').open_resource(address)
            self.instrument.write_termination = '\n'
            self.instrument.read_termination ='\n'
            self.instrument.timeout = timeout * 1000
            
    #def __init__(self, visa_addr="ASRL15:INSTR", lib=''):
    #rm = visa.ResourceManager(lib) # To use pyvisa-py backend, use argument '@py' self._visa = rm.open_resource(visa_addr)
    #self._visa = rm.open_resource(visa_addr, query_delay=0.01, timeout=0.1)
    #self._visa.write_termination = '\n'
    #self._visa.read_termination = '\n'
    # Set baudrate and stuff for serial communication only
    #if (visa_addr.find("ASRL") != -1):
    #    self._visa.baud_rate = 921600
    #    self._visa.send_end = False 

    #def query(self, cmd):
    #    return self._visa.query(cmd) 
    
    #def write(self, cmd):
    #    self._visa.write(cmd)

    def query(self, cmd):
        return self.instrument.query(cmd)
        
    def write_binary_values(self, cmd, values):
        self.instrument.write_binary_values(cmd, values)
        
    def reset(self):
        self.write('*rst')
                
    def set_range(self,channel,mode): #LOW (-2V~2V) HIGH (-10V~10V)
        self.write(f'SOUR:RANG {mode}, (@{channel})')
        
    def set_filter(self,channel,mode): #DC, MED, HIGH
        self.write(f'SOUR{channel}:FILT {mode}')
        
    def set_const_DC(self,channel,voltage):
        self.write(f'SOUR{channel}:DC:VOLT {voltage}')

    #### DS modified
    def query_filter(self,channel):
        return self.query(f'SOUR{channel}:FILT?')  

    def query_range(self,channel): 
        return self.query(f'SOUR{channel}:RANG?')

    def get_id(self):
        return self.query('*IDN?')
        
    def query_err(self):
        return self.query('syst:err:all?')
    
    def setup_channel(self, channel, voltages, tmod="STEP", mode="LIST", dc_trigger_source=None, marker_number=None):
        self.write(f'SOUR{channel}:LIST:VOLT {",".join(map(str, voltages))}')
        self.write(f'SOUR{channel}:LIST:TMOD {tmod}')
        self.write(f'SOUR{channel}:VOLT:MODE {mode}')
        if dc_trigger_source:
            self.write(f'SOUR{channel}:DC:TRIG:SOUR {dc_trigger_source}')
        if marker_number is not None:
            self.write(f'SOUR{channel}:DC:MARKER:START:TNUMBER {marker_number}')

    def set_continuous(self, channel, state):
        if state:
            state_str='ON'
        else:
            state_str='OFF'
        self.write(f'SOUR{channel}:DC:INIT:CONT {state_str}')


    def __exit__(self):
        self.close()
    
    #### DS Added
    def set_volt(self, channel, voltage):
        self.write(f'SOUR{channel}:DC:VOLT {voltage}')
        
    def get_volt(self, channel):
        return float(self.query('sour{channel}:dc:VOLT?')) #q.query('sour9:dc:VOLT?')
    
    def set_mode(self, channel, mode='fix'):
        self.write("sour{channel}:dc:mode {mode}")
        
