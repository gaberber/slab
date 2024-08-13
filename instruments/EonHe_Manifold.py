from slab.instruments.instrumenttypes import SocketInstrument, SerialInstrument
import os, time, sys
import numpy as np
import Pyro4

# This control is modified by Brennan for single arduino control and some operational conveniences

class EonHeManifold(SocketInstrument):
    DEBUG_HELIUM_MANIFOLD = True
    DEBUG_HELIUM_MANIFOLD_VERBOSE = True

    # These are the valve numbers as shown on the labels on the side of each valve
    gas_port = 1
    special_gas_port = 4
    pump_port = 3
    cryostat_port = 2

    atm_level = 340.6
    vacuum_offset = 0.
    vacuum_threshold = 0.03

    #removed pressurereadout serial instrument
    # def __init__(self, name="helium_manifold", address="192.168.14.173:80", enabled=True, recv_length=1024, timeout=1.0, **kwargs):
    #     SocketInstrument.__init__(self, name=name, address=address, enabled=enabled, recv_length=recv_length,
    #                                               timeout=timeout, **kwargs)
    #10.108.30.53:80
    def __init__(self, name="helium_manifold", address="10.108.30.53:80", enabled=True, recv_length=1024, timeout=1.0, **kwargs):
        SocketInstrument.__init__(self, name=name, address=address, enabled=enabled, recv_length=recv_length,
                                                  timeout=timeout, **kwargs)
    # def __init__(self, name="helium_manifold", address="10.108.30.53:80", enabled=True, recv_length=1024, **kwargs):
    #     SerialInstrument.__init__(self, name=name, address=address, baudrate=9600,
    #                                             enabled=enabled, recv_length=recv_length, timeout=0.15,
    #                                             query_sleep=0.10)
    # def __init__(self, name="helium_manifold", address="0.0.0.0:9090", enabled=True, recv_length=1024, timeout=1.0, **kwargs):
    #     SocketInstrument.__init__(self, name=name, address=address, enabled=enabled, recv_length=recv_length,
    #                                               timeout=timeout, **kwargs)

        # For the serial instrument, read() waits for timeout seconds and then responds with the answer.
        # Make sure to set this low enough such that the instrument responds quickly, but not so fast that
        # it leads to missing information.
        # self.PressureReadOut = SerialInstrument(name=name+"_pressure_readout", address="COM7", baudrate=9600,
        #                                         enabled=enabled, recv_length=recv_length, timeout=0.15,
        #                                         query_sleep=0.10)
        # self.PressureReadOut.term_char = '\r\n'

        self.term_char = '\n'
        self.set_query_sleep(0.1)
        self.puffs = 0
        # self.V_vac = 0.4692 #0.028
        self.V_vac = 0.4741  # 0.028
        self.V_1atm = 1.19 #1.2072
        # atm 2.219 new gauge
        # vac new gauge: 
        self.pressure_rise_log = list()

    def set_valve(self, valve_number, state):
        if state:
            self.open_valve(valve_number)
        else:
            self.close_valve(valve_number)

    def open_valve(self, valve_number):
        self.write("O%d\n"%valve_number)

    def close_valve(self, valve_number):
        self.write("C%d\n"%valve_number)

    def toggle_gas(self):
        self.write("T\n")

    def get_pressure(self):
        self.pressure = (self.get_transducer_voltage() - self.V_vac ) / (self.V_1atm - self.V_vac)
        print("pressure:")
        print(self.pressure)
        return self.pressure

    #rewrote for use with self and not serial instrument. not sure hwy the terminated characters are 2 here and not 1 like everywhere else. seems unnecessary
    def get_transducer_voltage(self):
        self.write("S3\n")
        # print(self.PressureReadOut.query_sleep)
        time.sleep(0.1)
        answer = self.read()
        print("voltage:")
        print(np.float(answer.strip('\r\n')))
        return np.float(answer.strip('\r\n'))
    # def get_transducer_voltage(self):
    #     self.PressureReadOut.write(r"S2\r\n")
    #     # print(self.PressureReadOut.query_sleep)
    #     time.sleep(self.PressureReadOut.query_sleep)
    #     answer = self.PressureReadOut.read()
    #     print(answer)
    #     return np.float(answer.strip('\r\n'))

    def get_manifold_status(self):
        self.get_manifold_status_bits()
        self.get_pressure()
        status_str = "gas: %s / Pump: %s / cryostat: %s / special gas: %s / Pressure: %f bar" % (
            str(self.gas_state), str(self.pump_state), str(self.cryostat_state), str(self.special_gas_state), self.pressure)
        return status_str

    def get_manifold_status_bits(self):
        """
        :return: a 1 for which output is open, a 0 for the output that is closed
        Order: gas, pump, cryostat
        """
        self.write("S1\n")
        time.sleep(self.query_sleep)
        # answer = "".join(self.read_line(eof_char='\r\n'))
        answer = "".join(self.read())
        v = answer.strip("\r\n")
        print("here")
        print(answer)
        print(v)
        print("here2")
        self.gas_state = np.int(v[self.gas_port-1])
        self.pump_state = np.int(v[self.pump_port-1])
        self.cryostat_state = np.int(v[self.cryostat_port-1])
        self.special_gas_state = np.int(v[self.special_gas_port - 1])
        print("gas:" + str(self.gas_state))
        print("pump:" + str(self.pump_state))
        print("cryostat:" + str(self.cryostat_state))
        print("special:" + str(self.special_gas_state))
        return self.gas_state, self.pump_state, self.cryostat_state, self.special_gas_state

    def set_special_gas(self, state=False, override=False):
        if not state or override:
            self.set_valve(self.special_gas_port, state)
        else:
            self.get_manifold_status()
            if self.pump_state or self.cryostat_state or self.gas_state:
                raise Exception("Unsafe operation attempted: Tried to open special gas port while other ports are open")
            else:
                self.set_valve(self.special_gas_port, state)
        self.get_manifold_status()

    def set_gas(self, state=False, override=False):
        if not state or override:
            self.set_valve(self.gas_port, state)
        else:
            self.get_manifold_status()
            if self.pump_state or self.cryostat_state or self.special_gas_state:
                raise Exception("Unsafe operation attempted: Tried to open gas while other ports open")
            else:
                self.set_valve(self.gas_port, state)
        # self.get_manifold_status()

    def set_pump(self, state=False, override=False):
        if not state or override:
            self.set_valve(self.pump_port, state)
        else:
            self.get_manifold_status()
            if self.gas_state or self.special_gas_state:
                raise Exception("Unsafe operation attempted: Tried to open pump port while gas port is open")
            else:
                self.set_valve(self.pump_port, state)
        self.get_manifold_status()

    def set_cryostat(self, state=False, override=False):
        if not state or override:
            self.set_valve(self.cryostat_port, state)
        else:
            self.get_manifold_status()
            if self.gas_state or self.special_gas_state:
                raise Exception("Unsafe operation attempted: Tried to cryostat port while gas port is open")
            else:
                self.set_valve(self.cryostat_port, state)
        self.get_manifold_status()

    def wait_for_pressure_rise(self, threshold, timeout=None):
        done = False
        self.pressure_rise_log = list()
        start_time = time.time()
        while not done:
            if self.DEBUG_HELIUM_MANIFOLD_VERBOSE:
                pressure = self.get_pressure()
                self.pressure_rise_log.append(time.time() - start_time)
                self.pressure_rise_log.append(pressure)
                sys.stdout.write('wait for pressure rise: %f\r' % (pressure))
                sys.stdout.flush()
            if self.get_pressure() > threshold: done = True
            if timeout is not None:
                if time.time() - start_time > timeout:
                    done = True
                    print("HeManifold Pressure timeout final P=%f bar" % self.get_pressure())
        self.pressure_rise_log = np.reshape(np.array(self.pressure_rise_log), (int(len(self.pressure_rise_log)/2), 2))

    def wait_for_pressure_fall(self, threshold, timeout=None):
        done = False
        start_time = time.time()
        while not done:
            if self.DEBUG_HELIUM_MANIFOLD_VERBOSE:
                pressure = self.get_pressure()
                sys.stdout.write('wait for pressure fall: %f\r' % (pressure))
                sys.stdout.flush()
            if self.get_pressure() < threshold: done = True
            if timeout is not None:
                if time.time() - start_time > timeout:
                    done = True
                    print("HeManifold Pressure timeout final P=%f bar" % self.get_pressure())
        self.get_manifold_status()

    def wait_for_vacuum(self, min_time=0, timeout=None):
        start_time = time.time()
        evacuated = False
        while not evacuated:
            self.wait_for_pressure_fall(self.vacuum_threshold, timeout)
            if (time.time() - start_time > min_time): evacuated = True

    def pump_manifold(self, min_time=0, timeout=None):
        if self.DEBUG_HELIUM_MANIFOLD: print("Pump manifold.")
        self.set_gas(False)
        self.set_special_gas(False)
        self.set_cryostat(False)
        self.set_pump(True)
        self.wait_for_vacuum(min_time=min_time, timeout=timeout)
        self.get_manifold_status()

    def pump_cryostat(self, min_time=0, timeout=None):
        if self.DEBUG_HELIUM_MANIFOLD: print("Pump cryostat.")
        self.set_gas(False)
        self.set_special_gas(False)
        self.set_cryostat(False)
        self.set_pump(True)
        self.wait_for_vacuum(min_time=min_time, timeout=timeout)
        self.set_cryostat(True)

    def fill_manifold(self, special_gas=False, prepump=False, fill_level=0.20, timeout=None):
        if self.DEBUG_HELIUM_MANIFOLD: print("Fill manifold to %f bar." % (fill_level))
        self.set_cryostat(False)
        self.set_pump(False)
        if special_gas:
            self.set_special_gas(True)
        else:
            self.set_gas(True)

        if prepump and not special_gas: #This pumps out the dead volume after the gas valve (Don't want to pump on 3-He gas)
            self.set_pump(True, override=True)
            self.wait_for_pressure_fall(threshold=fill_level, timeout=timeout)
            self.set_pump(False)
        self.wait_for_pressure_rise(fill_level, timeout=timeout)
        if special_gas:
            self.set_special_gas(False)
        else:
            self.set_gas(False)
        self.get_manifold_status()

    # def puff(self, pressure, n=1, min_time=0, special_puff=False, prepump=True, timeout=None):
    #     for i in range(n):
    #         if self.DEBUG_HELIUM_MANIFOLD: print("Puff #%d" % (self.puffs + 1))
    #         self.pump_manifold(min_time=min_time, timeout=timeout)
    #         self.fill_manifold(special_gas=special_puff, fill_level=pressure, prepump=prepump, timeout=timeout)
    #         self.set_cryostat(True)
    #         self.puffs += 1
    #         if self.DEBUG_HELIUM_MANIFOLD: print("Letting puff out.")
    #         self.wait_for_vacuum(min_time=min_time, timeout=timeout)
    #         self.set_cryostat(False)

    #puff without having to keep the pump connected or relying on a flange on the pump port
    # we refill the manifold anyways, so opening the pump port / pumping every puff isn't helpful
    def puff(self, pressure, n=1, min_time=0, special_puff=False, prepump=True, timeout=None):
        for i in range(n):
            if self.DEBUG_HELIUM_MANIFOLD: print("Puff #%d" % (self.puffs + 1))
            # self.pump_manifold(min_time=min_time, timeout=timeout)
            self.fill_manifold(special_gas=special_puff, fill_level=pressure, prepump=prepump, timeout=timeout)
            self.set_cryostat(True)
            self.puffs += 1
            if self.DEBUG_HELIUM_MANIFOLD: print("Letting puff out.")
            self.wait_for_vacuum(min_time=min_time, timeout=timeout)
            self.set_cryostat(False)

    def get_puffs(self):
        return self.puffs

    def set_puffs(self, puffs=0):
        self.puffs = puffs

    def clean_manifold(self, n=1, min_time=0, timeout=None):
        if self.DEBUG_HELIUM_MANIFOLD: print("Clean manifold %d times." % n)
        self.pump_manifold(min_time=min_time, timeout=timeout)
        for i in range(n):
            self.fill_manifold(timeout=timeout)
            self.pump_manifold(min_time=min_time, timeout=timeout)

    def seal_manifold(self):
        if self.DEBUG_HELIUM_MANIFOLD_VERBOSE: print("Seal manifold.")
        self.set_gas(False)
        self.set_special_gas(False)
        self.set_cryostat(False)
        self.set_pump(False)
        self.get_manifold_status()

if __name__ == '__main__':
    heman = EonHeManifold(address="192.168.14.173:80", query_sleep=0.01)
    # heman = EonHeManifold(address="192.168.14.173", query_sleep=0.05)
    #seal just in case
    print("HeMan Initialized")

    #I have no idea what this does other than show a fill over time graph. Gives an idea of fill speed, but doesn't seem so valuable
    def calibrate_metering_valve(threshold):
        from matplotlib import pyplot as plt

        heman.seal_manifold()
        heman.set_pump(True)
        time.sleep(5)
        print("Done pumping...")
        heman.seal_manifold()
        print("Opening gas...")
        heman.set_gas(True)

        t, p = list(), list()
        t0 = time.time()
        current_pressure = heman.get_pressure()
        while current_pressure < threshold:
            current_pressure = heman.get_pressure()
            current_time = time.time() - t0
            p.append(current_pressure)
            t.append(current_time)
            print("Time: %.1f s\t %.0f mbar"%(current_time, current_pressure*1E3))

        heman.seal_manifold()

        t_done = time.time()
        while time.time()-t_done < 5:
            current_time = time.time() - t0
            current_pressure = heman.get_pressure()
            p.append(current_pressure)
            t.append(current_time)
            print("Time: %.1f s\t %.0f mbar"%(current_time, current_pressure*1E3))

        fig=plt.figure(figsize=(6.,4.))
        plt.plot(t, np.array(p)*1E3, 'ob')
        plt.xlabel("Time (s)")
        plt.ylabel("Pressure (mbar)")
        plt.show()

        print("Final pressure: %.0f"%(heman.get_pressure()*1E3))

        print("Done")