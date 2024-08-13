from slab.instruments.instrumenttypes import SocketInstrument, SerialInstrument
import os, time, sys
import numpy as np
import Pyro4

# This control is modified by Brennan for single arduino control and some operational conveniences

class QDACII(SocketInstrument):
    def __init__(self, name="QDACII", address="10.108.30.68", enabled=True, recv_length=1024, timeout=1.0, **kwargs):
        SocketInstrument.__init__(self, name=name, address=address, enabled=enabled, recv_length=recv_length,
                                                  timeout=timeout, **kwargs)
        self.query_sleep = 0.05
        self.timeout = 100
        self.read_termination = '\n'

    