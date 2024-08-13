import serial
import time

class AD5764():

    voltages_mem = [0,0,0,0,0,0,0,0]
    def __init__(self, port='COM3'):
        self.instrument = serial.Serial(port=port, timeout=0)
        time.sleep(2)

    def set_voltage(self, channel, voltage):
        if channel == 1:
            n1 = 19
            n2 = 0
            m1 = 1
            m2 = 0
        elif channel == 2:
            n1 = 18
            n2 = 0
            m1 = 1
            m2 = 0
        elif channel == 3:
            n1 = 17
            n2 = 0
            m1 = 1
            m2 = 0
        elif channel == 4:
            n1 = 16
            n2 = 0
            m1 = 1
            m2 = 0
        elif channel == 5:
            n1 = 0
            n2 = 19
            m1 = 0
            m2 = 1
        elif channel == 6: 
            n1 = 0
            n2=18
            m1=0
            m2=1
        elif channel == 7:
            n1 = 0
            n2 = 17 
            m1 = 0
            m2 = 1
        elif channel == 8:
            n1 = 0
            n2 = 16
            m1 = 0
            m2 = 1
        else:
            print("Channel out of range")

        if voltage < 10 and voltage >= 0:
            dec16 = int(round((2**15-1)*voltage/10)) #Decimal equivalent of 16 bit data 
        elif voltage < 0 and voltage > -10:
            dec16 = int(round(2**16 - abs(voltage)/10 * 2**15))
        else:
            print("Voltage out of range")
            return
        binary_num = format(dec16, '016b')
        d1 = int(binary_num[:8], 2)
        d2 = int(binary_num[8:], 2)
        command = bytes([255, 254, 253, n1, d1*m1, d2*m1, n2, d1*m2, d2*m2])
        # print(command)
        # print(f'Set ch {channel} to {voltage} volts')
        self.instrument.write(command)        
        print(f'Set ch {channel} to {voltage} volts')

        voltages_mem[channel-1]=voltage

    def initialize(self):
        for i in range(8):
            self.set_voltage(i+1, 0)
            time.sleep(0.1)
            
    def close(self):
        self.instrument.close()

    #AD5764 base arduino driver has no method to read voltages and i haven't written one yet, so this is the closest we have atm
    def recall_voltages(self):
        return voltages_mem